import logging

from django.db import transaction
from django.db.models import Exists, OuterRef
from rest_framework.parsers import FormParser, MultiPartParser

from meetups.views.helpers import APIResponse

from ..models import ChatMessage, ChatRoom, LiteConfig, Rsvp, SeminarRequest
from ..serializers import message_obj
from ..throttles import MessageSendThrottle
from ..uploads import validate_attachment
from .base import ApiError, LiteView, clean_text, get_or_404

logger = logging.getLogger(__name__)

MESSAGE_LIMIT = 200
INITIAL_MESSAGE_LIMIT = 100
MAX_AFTER = 2**63 - 1


def room_with_access(room_id, member):
    """채팅방과 접근 권한을 한 번의 쿼리로 조회한다. 권한이 없으면 403, 방이 없으면 404."""
    room = get_or_404(
        ChatRoom.objects.select_related('seminar', 'pinned_message__member').annotate(
            has_rsvp=Exists(
                Rsvp.objects.filter(
                    member=member, meetup_id=OuterRef('meetup_id'),
                    status__in=[Rsvp.Status.GOING, Rsvp.Status.MAYBE],
                )
            )
        ),
        '채팅방을 찾을 수 없어요',
        pk=room_id,
    )
    if member.is_host:
        allowed = True
    elif room.kind == ChatRoom.Kind.MEETUP:
        allowed = room.has_rsvp
    else:
        allowed = room.seminar.member_id == member.id
    if not allowed:
        raise ApiError('이 채팅방에 들어갈 수 없어요', 403)
    return room


def parse_message_id(raw, name):
    if not (raw.isascii() and raw.isdigit()) or int(raw) > MAX_AFTER:
        raise ApiError(f'{name} 값이 올바르지 않아요')
    return int(raw)


def latest_page(qs, limit):
    """가장 최근 limit개를 id 오름차순으로 돌려준다. 하나 더 읽어서 더 오래된 메시지가 남았는지 판단한다."""
    rows = list(qs.order_by('-id')[:limit + 1])
    return rows[:limit][::-1], len(rows) > limit


class RoomMessagesView(LiteView):
    throttle_classes = [MessageSendThrottle]  # 폴링(GET)은 제한하지 않고 전송(POST)만 센다

    def _room(self, room_id):
        return room_with_access(room_id, self.member)

    def get(self, request, room_id):
        room = self._room(room_id)
        after = request.query_params.get('after')
        before = request.query_params.get('before')
        qs = ChatMessage.objects.select_related('member').filter(room=room)
        pinned = message_obj(room.pinned_message) if room.pinned_message_id else None
        if after not in (None, ''):
            messages = list(qs.filter(id__gt=parse_message_id(after, 'after')).order_by('id')[:MESSAGE_LIMIT])
            return APIResponse.success({'messages': [message_obj(m) for m in messages], 'pinned': pinned})
        if before not in (None, ''):
            qs = qs.filter(id__lt=parse_message_id(before, 'before'))
        messages, has_more = latest_page(qs, INITIAL_MESSAGE_LIMIT)
        return APIResponse.success({'messages': [message_obj(m) for m in messages], 'has_more': has_more, 'pinned': pinned})

    def post(self, request, room_id):
        room = self._room(room_id)
        member = self.member
        body = clean_text(self.json_body().get('body'), '메시지', 1, 1000)
        with transaction.atomic():
            message = ChatMessage.objects.create(room=room, member=member, kind=ChatMessage.Kind.USER, body=body)
            if room.kind == ChatRoom.Kind.SEMINAR:
                seminar = SeminarRequest.objects.select_for_update().get(pk=room.seminar_id)
                if (
                    seminar.member_id == member.id
                    and seminar.status == SeminarRequest.Status.GUIDE
                    and seminar.mode
                ):
                    seminar.topic = body
                    seminar.status = SeminarRequest.Status.RECEIVED
                    seminar.save(update_fields=['topic', 'status'])
                    ChatMessage.objects.create(
                        room=room, kind=ChatMessage.Kind.GUIDE, body=LiteConfig.get().seminar_guide_4
                    )
                    logger.info('LITE 세미나 접수: seminar_id=%s', seminar.id)
        return APIResponse.created({'message': message_obj(message)})


class RoomFilesView(LiteView):
    parser_classes = [MultiPartParser, FormParser]
    throttle_classes = [MessageSendThrottle]

    def post(self, request, room_id):
        room = room_with_access(room_id, self.member)
        data = self.json_body()
        upload = request.FILES.get('file')
        raw_body = data.get('body') or ''
        body = clean_text(raw_body, '메시지', 0, 1000) if raw_body else ''
        info = validate_attachment(upload)
        message = ChatMessage.objects.create(
            room=room, member=self.member, kind=ChatMessage.Kind.USER, body=body, attachment=upload, **info
        )
        return APIResponse.created({'message': message_obj(message)})
