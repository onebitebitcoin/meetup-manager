import logging
from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from meetups.views.helpers import APIResponse

from ..auth import IsHost
from ..models import ChatMessage, LiteConfig, Meetup, MeetupRequest, Rsvp
from ..serializers import meetup_card, my_statuses, seminar_card
from ..services import (
    KST,
    add_message,
    is_today,
    meetups_with_counts,
    requests_with_votes,
    seminars_with_last_message,
    today_start_kst,
)
from ..throttles import CheckinThrottle
from .base import ApiError, LiteView, clean_text, get_or_404

logger = logging.getLogger(__name__)

MIN_YEAR = 2000
MAX_YEAR = 2100
MEETUP_END_GRACE = timedelta(hours=12)
DESCRIPTION_MAX = 1000

RSVP_LABELS = {Rsvp.Status.GOING: '참석', Rsvp.Status.MAYBE: '미정', Rsvp.Status.NO: '불참'}


def card_for(meetup_id, member):
    meetup = meetups_with_counts().get(pk=meetup_id)
    return meetup_card(meetup, my_statuses(member, [meetup_id]).get(meetup_id))


def parse_starts_at(value):
    if not isinstance(value, str):
        raise ApiError('시작 시각을 입력해 주세요')
    try:
        parsed = parse_datetime(value.strip())
    except ValueError:
        parsed = None
    if parsed is None:
        raise ApiError('시작 시각 형식이 올바르지 않아요')
    if not MIN_YEAR <= parsed.year <= MAX_YEAR:
        raise ApiError('시작 시각의 연도가 올바르지 않아요')
    if timezone.is_naive(parsed):
        parsed = parsed.replace(tzinfo=KST)
    try:
        in_range = MIN_YEAR <= parsed.astimezone(KST).year <= MAX_YEAR
    except OverflowError:
        in_range = False
    if not in_range:
        raise ApiError('시작 시각의 연도가 올바르지 않아요')
    return parsed


def parse_capacity(value):
    if isinstance(value, bool):
        raise ApiError('정원은 2~500명 사이로 입력해 주세요')
    try:
        capacity = int(value)
    except (TypeError, ValueError):
        raise ApiError('정원은 2~500명 사이로 입력해 주세요') from None
    if not 2 <= capacity <= 500:
        raise ApiError('정원은 2~500명 사이로 입력해 주세요')
    return capacity


class HomeView(LiteView):
    def get(self, request):
        member = self.member
        meetups = list(meetups_with_counts().filter(starts_at__gte=today_start_kst()).order_by('starts_at', 'id'))
        mine = my_statuses(member, [m.id for m in meetups])
        my_seminar = seminars_with_last_message().filter(member=member).first()
        seminars = []
        if member.is_host:
            seminars = [seminar_card(s) for s in seminars_with_last_message().order_by('-id')]
        threshold = LiteConfig.get().vote_threshold
        ready = requests_with_votes().filter(status=MeetupRequest.Status.OPEN, vote_count__gte=threshold).count()
        return APIResponse.success({
            'meetups': [meetup_card(m, mine.get(m.id)) for m in meetups],
            'my_seminar': seminar_card(my_seminar) if my_seminar else None,
            'seminars': seminars,
            'ready_request_count': ready,
        })


class MeetupCreateView(LiteView):
    permission_classes = [IsHost]

    def post(self, request):
        data = self.json_body()
        title = clean_text(data.get('title'), '제목', 1, 80)
        location = clean_text(data.get('location'), '장소', 1, 100)
        starts_at = parse_starts_at(data.get('starts_at'))
        capacity = parse_capacity(data.get('capacity'))
        if starts_at <= timezone.now():
            raise ApiError('시작 시각은 현재 이후여야 해요')
        description = data.get('description') or ''
        if not isinstance(description, str):
            raise ApiError('설명 형식이 올바르지 않아요')
        if len(description.strip()) > DESCRIPTION_MAX:
            raise ApiError(f'설명은 {DESCRIPTION_MAX}자 이내로 입력해 주세요')
        request_id = data.get('request_id')

        with transaction.atomic():
            req = None
            if request_id not in (None, ''):
                req = MeetupRequest.objects.select_for_update().filter(pk=_to_int(request_id)).first()
                if req is None:
                    raise ApiError('요청을 찾을 수 없어요', 404)
                if req.status != MeetupRequest.Status.OPEN:
                    raise ApiError('이미 모임이 열린 요청이에요')
            meetup = Meetup.objects.create(
                title=title, description=description.strip(), starts_at=starts_at,
                location=location, capacity=capacity, from_request=req,
            )
            if req is not None:
                req.status = MeetupRequest.Status.DONE
                req.meetup = meetup
                req.save(update_fields=['status', 'meetup'])
                add_message(meetup.room, f'요청으로 열린 모임이에요 · {req.votes.count()}명에게 알림')
        logger.info('LITE 모임 생성: id=%s request_id=%s', meetup.id, req.id if req else None)
        return APIResponse.created({'meetup': card_for(meetup.id, self.member)})


def _to_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        raise ApiError('요청 ID가 올바르지 않아요') from None


class MeetupDetailView(LiteView):
    def get(self, request, meetup_id):
        member = self.member
        meetup = get_or_404(meetups_with_counts(), '모임을 찾을 수 없어요', pk=meetup_id)
        rsvp = Rsvp.objects.filter(member=member, meetup=meetup).first()
        show_code = member.is_host and is_today(meetup.starts_at)
        return APIResponse.success({
            'meetup': meetup_card(meetup, rsvp.status if rsvp else None),
            'checkin_code': meetup.checkin_code if show_code else None,
            'checked_in': bool(rsvp and rsvp.checked_in_at),
            'checked_in_count': Rsvp.objects.filter(meetup=meetup, checked_in_at__isnull=False).count(),
        })


class RsvpView(LiteView):
    def put(self, request, meetup_id):
        member = self.member
        new_status = self.json_body().get('status')
        if new_status not in RSVP_LABELS:
            raise ApiError('참석 상태는 going, maybe, no 중 하나여야 해요')
        with transaction.atomic():
            meetup = get_or_404(Meetup.objects.select_for_update(), '모임을 찾을 수 없어요', pk=meetup_id)
            if meetup.starts_at + MEETUP_END_GRACE < timezone.now():
                raise ApiError('이미 끝난 모임이에요')
            rsvp = Rsvp.objects.filter(member=member, meetup=meetup).first()
            previous = rsvp.status if rsvp else None
            if previous != new_status:
                if new_status == Rsvp.Status.GOING:
                    going = Rsvp.objects.filter(meetup=meetup, status=Rsvp.Status.GOING).count()
                    if going >= meetup.capacity:
                        raise ApiError('정원이 찼어요', 409)
                if rsvp is None:
                    rsvp = Rsvp.objects.create(member=member, meetup=meetup, status=new_status)
                else:
                    rsvp.status = new_status
                    rsvp.save(update_fields=['status', 'updated_at'])
                room = meetup.room
                add_message(room, f'{member.name}님 {RSVP_LABELS[new_status]}')
                joined = new_status in (Rsvp.Status.GOING, Rsvp.Status.MAYBE)
                if joined and previous in (None, Rsvp.Status.NO):
                    add_message(room, LiteConfig.get().join_guide, kind=ChatMessage.Kind.GUIDE)
        return APIResponse.success({'meetup': card_for(meetup.id, member)})


class CheckinView(LiteView):
    throttle_classes = [CheckinThrottle]

    def post(self, request, meetup_id):
        member = self.member
        code = self.json_body().get('code')
        meetup = get_or_404(Meetup.objects.select_related('room'), '모임을 찾을 수 없어요', pk=meetup_id)
        with transaction.atomic():
            rsvp = Rsvp.objects.select_for_update().filter(member=member, meetup=meetup).first()
            if rsvp is None or rsvp.status == Rsvp.Status.NO:
                raise ApiError('먼저 참석을 신청해 주세요', 403)
            if not is_today(meetup.starts_at):
                raise ApiError('오늘 열리는 모임이 아니에요')
            if not isinstance(code, str) or code.strip() != meetup.checkin_code:
                raise ApiError('코드가 달라요')
            if rsvp.checked_in_at is None:
                rsvp.checked_in_at = timezone.now()
                rsvp.save(update_fields=['checked_in_at', 'updated_at'])
                add_message(meetup.room, f'{member.name}님 도착')
        return APIResponse.success({'checked_in': True})

