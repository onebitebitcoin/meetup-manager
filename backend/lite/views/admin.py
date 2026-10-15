import logging

from django.db import transaction
from django.utils import timezone

from meetups.views.helpers import APIResponse

from ..auth import IsHost
from ..models import ChatMessage, ChatRoom, Meetup, Rsvp
from ..serializers import meetup_card, member_brief, message_obj
from ..services import KST, add_message, meetups_with_counts, today_start_kst
from .base import ApiError, LiteView, clean_text, get_or_404, not_found
from .meetups import DESCRIPTION_MAX, parse_capacity, parse_starts_at

logger = logging.getLogger(__name__)

IMAGE_URL_MAX = 500
IMAGE_URL_PREFIXES = ('http://', 'https://', '/media/')
WEEKDAYS = '월화수목금토일'
STATUS_ORDER = {Rsvp.Status.GOING: 0, Rsvp.Status.MAYBE: 1, Rsvp.Status.NO: 2}


def format_schedule(starts_at, location):
    local = starts_at.astimezone(KST)
    when = f'{local.month}월 {local.day}일 ({WEEKDAYS[local.weekday()]}) {local:%H:%M}'
    return f'일정이 바뀌었어요 · {when} · {location}'


def parse_image_url(value):
    if not isinstance(value, str):
        raise ApiError('썸네일 주소 형식이 올바르지 않아요')
    value = value.strip()
    if len(value) > IMAGE_URL_MAX:
        raise ApiError(f'썸네일 주소는 {IMAGE_URL_MAX}자 이내로 입력해 주세요')
    if value and not value.startswith(IMAGE_URL_PREFIXES):
        raise ApiError('썸네일 주소는 http://, https:// 또는 /media/로 시작해야 해요')
    return value


def parse_description(value):
    if not isinstance(value, str):
        raise ApiError('설명 형식이 올바르지 않아요')
    value = value.strip()
    if len(value) > DESCRIPTION_MAX:
        raise ApiError(f'설명은 {DESCRIPTION_MAX}자 이내로 입력해 주세요')
    return value


def locked_meetup(meetup_id):
    queryset = Meetup.objects.select_for_update().select_related('room')
    return get_or_404(queryset, '모임을 찾을 수 없어요', pk=meetup_id)


def admin_detail(meetup_id):
    meetup = get_or_404(meetups_with_counts(), '모임을 찾을 수 없어요', pk=meetup_id)
    rsvps = list(Rsvp.objects.filter(meetup=meetup).select_related('member').order_by('updated_at', 'id'))
    rsvps.sort(key=lambda r: STATUS_ORDER[r.status])
    attendees = [
        {
            'member': member_brief(r.member),
            'status': r.status,
            'checked_in_at': r.checked_in_at.isoformat() if r.checked_in_at else None,
            'removed': r.removed_at is not None,
        }
        for r in rsvps
    ]
    return {
        'meetup': meetup_card(meetup),
        'description': meetup.description,
        'image_url': meetup.image_url,
        'checkin_code': meetup.checkin_code,
        'attendees': attendees,
    }


def apply_meetup_changes(meetup, data):
    """보낸 필드만 검증해 meetup에 반영하고 바뀐 필드 이름 목록을 돌려준다."""
    changes = {}
    if 'title' in data:
        changes['title'] = clean_text(data['title'], '제목', 1, 80)
    if 'location' in data:
        changes['location'] = clean_text(data['location'], '장소', 1, 100)
    if 'starts_at' in data:
        changes['starts_at'] = parse_starts_at(data['starts_at'])
    if 'capacity' in data:
        capacity = parse_capacity(data['capacity'])
        going = Rsvp.objects.filter(meetup=meetup, status=Rsvp.Status.GOING).count()
        if capacity < going:
            raise ApiError(f'정원은 현재 참석 인원({going}명)보다 작게 줄일 수 없어요')
        changes['capacity'] = capacity
    if 'description' in data:
        changes['description'] = parse_description(data['description'])
    if 'image_url' in data:
        changes['image_url'] = parse_image_url(data['image_url'])
    changed = [name for name, value in changes.items() if getattr(meetup, name) != value]
    for name in changed:
        setattr(meetup, name, changes[name])
    return changed


class AdminMeetupListView(LiteView):
    permission_classes = [IsHost]

    def get(self, request):
        scope = request.query_params.get('scope', 'upcoming')
        if scope not in ('upcoming', 'past'):
            raise ApiError('scope는 upcoming, past 중 하나여야 해요')
        start = today_start_kst()
        if scope == 'upcoming':
            meetups = meetups_with_counts().filter(starts_at__gte=start).order_by('starts_at', 'id')
        else:
            meetups = meetups_with_counts().filter(starts_at__lt=start).order_by('-starts_at', '-id')
        return APIResponse.success({'meetups': [meetup_card(m) for m in meetups]})


class AdminMeetupDetailView(LiteView):
    permission_classes = [IsHost]

    def get(self, request, meetup_id):
        return APIResponse.success(admin_detail(meetup_id))

    def patch(self, request, meetup_id):
        data = self.json_body()
        with transaction.atomic():
            meetup = locked_meetup(meetup_id)
            changed = apply_meetup_changes(meetup, data)
            if changed:
                meetup.save(update_fields=changed)
            if 'starts_at' in changed or 'location' in changed:
                add_message(meetup.room, format_schedule(meetup.starts_at, meetup.location))
        logger.info('LITE 모임 수정: id=%s fields=%s', meetup_id, changed)
        return APIResponse.success(admin_detail(meetup_id))

    def delete(self, request, meetup_id):
        meetup = get_or_404(Meetup.objects, '모임을 찾을 수 없어요', pk=meetup_id)
        meetup.delete()
        logger.info('LITE 모임 삭제: id=%s', meetup_id)
        return APIResponse.success({'deleted': True})


class AdminMeetupCancelView(LiteView):
    permission_classes = [IsHost]

    def post(self, request, meetup_id):
        cancelled = self.json_body().get('cancelled')
        if not isinstance(cancelled, bool):
            raise ApiError('cancelled는 true 또는 false여야 해요')
        with transaction.atomic():
            meetup = locked_meetup(meetup_id)
            if cancelled != (meetup.cancelled_at is not None):
                meetup.cancelled_at = timezone.now() if cancelled else None
                meetup.save(update_fields=['cancelled_at'])
                add_message(meetup.room, '모임이 취소됐어요' if cancelled else '모임이 다시 열렸어요')
                logger.info('LITE 모임 취소 변경: id=%s cancelled=%s', meetup_id, cancelled)
        return APIResponse.success(admin_detail(meetup_id))


class AdminMemberRemoveView(LiteView):
    permission_classes = [IsHost]

    def delete(self, request, meetup_id, member_id):
        get_or_404(Meetup.objects, '모임을 찾을 수 없어요', pk=meetup_id)
        rsvp = get_or_404(Rsvp.objects, '참석 신청한 회원이 아니에요', meetup_id=meetup_id, member_id=member_id)
        rsvp.status = Rsvp.Status.NO
        rsvp.removed_at = timezone.now()
        rsvp.save(update_fields=['status', 'removed_at', 'updated_at'])
        logger.info('LITE 참석자 내보내기: meetup_id=%s member_id=%s', meetup_id, member_id)
        return APIResponse.success(admin_detail(meetup_id))


class AdminMessageDeleteView(LiteView):
    permission_classes = [IsHost]

    def delete(self, request, room_id, message_id):
        message = get_or_404(ChatMessage.objects, '메시지를 찾을 수 없어요', pk=message_id, room_id=room_id)
        message.delete()
        logger.info('LITE 메시지 삭제: room_id=%s message_id=%s', room_id, message_id)
        return APIResponse.success({'deleted': True})


class AdminPinView(LiteView):
    permission_classes = [IsHost]

    def put(self, request, room_id):
        room = get_or_404(ChatRoom.objects, '채팅방을 찾을 수 없어요', pk=room_id)
        message_id = self.json_body().get('message_id')
        if message_id is None:
            message = None
        elif isinstance(message_id, int) and not isinstance(message_id, bool):
            message = ChatMessage.objects.select_related('member').filter(pk=message_id, room=room).first()
            if message is None:
                raise not_found('메시지를 찾을 수 없어요')
        else:
            raise ApiError('message_id 값이 올바르지 않아요')
        room.pinned_message = message
        room.save(update_fields=['pinned_message'])
        logger.info('LITE 공지 고정: room_id=%s message_id=%s', room_id, message_id)
        return APIResponse.success({'pinned': message_obj(message) if message else None})
