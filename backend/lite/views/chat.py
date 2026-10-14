import logging

from django.db import transaction
from django.db.models import Exists, OuterRef

from meetups.views.helpers import APIResponse

from ..models import ChatMessage, ChatRoom, LiteConfig, Rsvp, SeminarRequest
from ..serializers import message_obj
from ..throttles import MessageSendThrottle
from .base import ApiError, LiteView, clean_text, get_or_404

logger = logging.getLogger(__name__)

MESSAGE_LIMIT = 200
INITIAL_MESSAGE_LIMIT = 100
MAX_AFTER = 2**63 - 1


def room_with_access(room_id, member):
    """채팅방과 접근 권한을 한 번의 쿼리로 조회한다. 권한이 없으면 403, 방이 없으면 404."""
    room = get_or_404(
        ChatRoom.objects.select_related('seminar').annotate(
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


def parse_after(raw):
    if not (raw.isascii() and raw.isdigit()) or int(raw) > MAX_AFTER:
        raise ApiError('after 값이 올바르지 않아요')
    return int(raw)


class RoomMessagesView(LiteView):
    throttle_classes = [MessageSendThrottle]  # 폴링(GET)은 제한하지 않고 전송(POST)만 센다

    def _room(self, room_id):
        return room_with_access(room_id, self.member)

    def get(self, request, room_id):
        room = self._room(room_id)
        after = request.query_params.get('after')
        qs = ChatMessage.objects.select_related('member').filter(room=room)
        if after in (None, ''):
            messages = list(qs.order_by('-id')[:INITIAL_MESSAGE_LIMIT])[::-1]
        else:
            messages = list(qs.filter(id__gt=parse_after(after)).order_by('id')[:MESSAGE_LIMIT])
        return APIResponse.success({'messages': [message_obj(m) for m in messages]})

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
