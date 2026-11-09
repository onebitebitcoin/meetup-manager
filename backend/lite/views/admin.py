import logging
from urllib.parse import urlsplit

from django.contrib.auth.hashers import check_password, make_password
from django.db import IntegrityError, transaction
from django.utils import timezone

from meetups.views.helpers import APIResponse

from ..auth import IsHost
from ..models import ChatMessage, ChatRoom, LiteConfig, Meetup, Rsvp
from ..serializers import meetup_card, member_brief, member_full, message_obj
from ..services import KST, add_message, meetups_with_counts, rooms_for_host, today_start_kst
from ..throttles import AdminLoginThrottle, AdminPasswordThrottle
from ..thumbnails import ThumbnailError, make_thumbnail
from .base import ApiError, LiteView, clean_text, get_or_404, not_found
from .meetups import DESCRIPTION_MAX, parse_audience, parse_capacity, parse_starts_at

logger = logging.getLogger(__name__)

IMAGE_URL_MAX = 500
MEDIA_PREFIX = '/media/'
WEEKDAYS = '월화수목금토일'
STATUS_ORDER = {Rsvp.Status.GOING: 0, Rsvp.Status.MAYBE: 1, Rsvp.Status.NO: 2}


def format_schedule(starts_at, location):
    local = starts_at.astimezone(KST)
    when = f'{local.month}월 {local.day}일 ({WEEKDAYS[local.weekday()]}) {local:%H:%M}'
    return f'일정이 바뀌었어요 · {when} · {location}'


def is_valid_image_url(value):
    if any(ch.isspace() or ord(ch) < 32 or ord(ch) == 127 for ch in value):
        return False
    if value.startswith(MEDIA_PREFIX):
        return not any(bad in value for bad in ('//', '..', '\\'))
    try:
        parts = urlsplit(value)
    except ValueError:
        return False
    return parts.scheme in ('http', 'https') and bool(parts.netloc)


def parse_image_url(value):
    if not isinstance(value, str):
        raise ApiError('썸네일 주소 형식이 올바르지 않아요')
    if len(value) > IMAGE_URL_MAX:
        raise ApiError(f'썸네일 주소는 {IMAGE_URL_MAX}자 이내로 입력해 주세요')
    if value and not is_valid_image_url(value):
        raise ApiError('썸네일 주소는 http://, https:// 또는 /media/로 시작하는 올바른 주소여야 해요')
    return value


def thumbnail_for(data):
    """image_url을 보냈으면 썸네일 /media/ 주소를 만들어 돌려준다(비우면 ''). 안 보냈으면 None."""
    if 'image_url' not in data:
        return None
    image_url = parse_image_url(data['image_url'])
    if not image_url:
        return ''
    try:
        return make_thumbnail(image_url)
    except ThumbnailError as exc:
        raise ApiError(str(exc)) from exc


def parse_description(value):
    if not isinstance(value, str):
        raise ApiError('설명 형식이 올바르지 않아요')
    value = value.strip()
    if len(value) > DESCRIPTION_MAX:
        raise ApiError(f'설명은 {DESCRIPTION_MAX}자 이내로 입력해 주세요')
    return value


def locked_meetup(meetup_id):
    queryset = Meetup.objects.select_for_update()
    return get_or_404(queryset, '모임을 찾을 수 없어요', pk=meetup_id)


def admin_detail(meetup_id):
    meetup = get_or_404(meetups_with_counts(), '모임을 찾을 수 없어요', pk=meetup_id)
    rsvps = list(Rsvp.objects.filter(meetup=meetup).select_related('member').order_by('updated_at', 'id'))
    rsvps.sort(key=lambda r: STATUS_ORDER[r.status])
    attendees = [
        {
            'member': member_brief(r.member),
            'status': r.status,
        }
        for r in rsvps
    ]
    return {
        'meetup': meetup_card(meetup),
        'description': meetup.description,
        'audience': meetup.audience,
        'image_url': meetup.image_url,
        'attendees': attendees,
    }


def apply_meetup_changes(meetup, data, thumb_url=None):
    """보낸 필드만 검증해 meetup에 반영하고 바뀐 필드 이름 목록을 돌려준다. thumb_url은 thumbnail_for()의 결과."""
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
    if 'audience' in data:
        changes['audience'] = parse_audience(data['audience'])
    if 'image_url' in data:
        changes['image_url'] = parse_image_url(data['image_url'])
        changes['thumb_url'] = thumb_url
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
        # 이미지 내려받기는 느릴 수 있으므로 행 잠금을 잡기 전에 썸네일을 만든다
        thumb_url = thumbnail_for(data)
        with transaction.atomic():
            meetup = locked_meetup(meetup_id)
            changed = apply_meetup_changes(meetup, data, thumb_url)
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
        with transaction.atomic():
            locked_meetup(meetup_id)
            rsvp = get_or_404(
                Rsvp.objects.select_for_update(), '참석 신청한 회원이 아니에요', meetup_id=meetup_id, member_id=member_id
            )
            rsvp.delete()
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
        data = self.json_body()
        if 'message_id' not in data:
            raise ApiError('message_id가 필요해요')
        message_id = data['message_id']
        if message_id is None:
            message = None
        elif isinstance(message_id, int) and not isinstance(message_id, bool):
            message = get_or_404(
                ChatMessage.objects.select_related('member'), '메시지를 찾을 수 없어요', pk=message_id, room=room
            )
        else:
            raise ApiError('message_id 값이 올바르지 않아요')
        try:
            with transaction.atomic():
                room.pinned_message = message
                room.save(update_fields=['pinned_message'])
        except IntegrityError:
            raise not_found('메시지를 찾을 수 없어요') from None
        logger.info('LITE 공지 고정: room_id=%s message_id=%s', room_id, message_id)
        return APIResponse.success({'pinned': message_obj(message) if message else None})


class AdminOpenView(LiteView):
    permission_classes = [IsHost]

    def put(self, request):
        is_open = self.json_body().get('is_open')
        if not isinstance(is_open, bool):
            raise ApiError('is_open은 true 또는 false여야 해요')
        config = LiteConfig.get()
        config.is_open = is_open
        config.save(update_fields=['is_open'])
        logger.info('LITE 오픈 상태 변경: is_open=%s member_id=%s', is_open, self.member.id)
        return APIResponse.success({'is_open': is_open})


PASSWORD_MIN = 8
PASSWORD_MAX = 128
GUIDE_FIELDS = ('seminar_guide_1', 'seminar_guide_2', 'seminar_guide_3', 'seminar_guide_4', 'join_guide')
SETTING_FIELDS = ('vote_threshold', *GUIDE_FIELDS)
GUIDE_MAX = 1000
VOTE_THRESHOLD_MAX = 1000


def config_settings(config):
    return {name: getattr(config, name) for name in SETTING_FIELDS}


class AdminLoginView(LiteView):
    """비밀번호가 맞으면 요청한 회원을 운영자로 바꾼다. 오픈 전 잠금과 무관하다."""

    throttle_classes = [AdminLoginThrottle]

    def post(self, request):
        password = self.json_body().get('password')
        if not isinstance(password, str) or not check_password(password, LiteConfig.get().admin_password_hash):
            logger.warning('LITE 운영자 로그인 실패: member_id=%s', self.member.id)
            raise ApiError('비밀번호가 맞지 않아요', 403)
        member = self.member
        if not member.is_host:
            member.is_host = True
            member.save(update_fields=['is_host'])
            logger.info('LITE 운영자 로그인으로 승격: member_id=%s', member.id)
        return APIResponse.success({'member': member_full(member)})


class AdminPasswordView(LiteView):
    permission_classes = [IsHost]
    throttle_classes = [AdminPasswordThrottle]

    def put(self, request):
        data = self.json_body()
        current, new = data.get('current_password'), data.get('new_password')
        config = LiteConfig.get()
        if not isinstance(current, str) or not check_password(current, config.admin_password_hash):
            logger.warning('LITE 비밀번호 변경 실패: member_id=%s', self.member.id)
            raise ApiError('현재 비밀번호가 맞지 않아요', 403)
        if not isinstance(new, str) or len(new) < PASSWORD_MIN:
            raise ApiError(f'새 비밀번호는 {PASSWORD_MIN}자 이상이어야 해요')
        if len(new) > PASSWORD_MAX:
            raise ApiError(f'새 비밀번호는 {PASSWORD_MAX}자 이내로 입력해 주세요')
        config.admin_password_hash = make_password(new)
        config.save(update_fields=['admin_password_hash'])
        logger.info('LITE 운영자 비밀번호 변경: member_id=%s', self.member.id)
        return APIResponse.success({'changed': True})


class AdminSettingsView(LiteView):
    permission_classes = [IsHost]

    def get(self, request):
        return APIResponse.success(config_settings(LiteConfig.get()))

    def patch(self, request):
        data = self.json_body()
        unknown = sorted(set(data) - set(SETTING_FIELDS))
        if unknown:
            raise ApiError(f'바꿀 수 없는 항목이에요: {", ".join(unknown)}')
        values = {}
        for name, value in data.items():
            if name == 'vote_threshold':
                if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= VOTE_THRESHOLD_MAX:
                    raise ApiError(f'투표 기준 인원은 1~{VOTE_THRESHOLD_MAX} 사이 숫자여야 해요')
            else:
                if not isinstance(value, str) or not value.strip():
                    raise ApiError('안내 문구를 입력해 주세요')
                if len(value) > GUIDE_MAX:
                    raise ApiError(f'안내 문구는 {GUIDE_MAX}자 이내로 입력해 주세요')
            values[name] = value
        config = LiteConfig.get()
        for name, value in values.items():
            setattr(config, name, value)
        if values:
            config.save(update_fields=list(values))
            logger.info('LITE 설정 변경: fields=%s member_id=%s', sorted(values), self.member.id)
        return APIResponse.success(config_settings(config))


class AdminRoomListView(LiteView):
    """모임 방과 세미나 방을 한 목록으로. 최근 메시지가 있는 방이 먼저, 최대 100개."""

    permission_classes = [IsHost]

    def get(self, request):
        rooms = []
        for room in rooms_for_host(self.member):
            item = {
                'room_id': room.id,
                'kind': room.kind,
                'last_message': (
                    {'body': room.last_body, 'created_at': room.last_at.isoformat()} if room.last_at else None
                ),
                'unread_count': room.unread,
            }
            if room.kind == ChatRoom.Kind.MEETUP and room.meetup:
                item.update(
                    title=room.meetup.title, meetup_id=room.meetup_id,
                    cancelled=room.meetup.cancelled_at is not None,
                    starts_at=room.meetup.starts_at.isoformat(),
                )
            elif room.kind == ChatRoom.Kind.SEMINAR and room.seminar:
                item.update(title=f'1:1 · {room.seminar.member.name}', seminar_id=room.seminar_id, cancelled=False)
            else:
                continue
            rooms.append(item)
        return APIResponse.success({'rooms': rooms})
