import logging

from django.db import transaction

from meetups.views.helpers import APIResponse

from ..models import ChatMessage, ChatRoom, LiteConfig, Rsvp, SeminarRequest
from ..serializers import message_obj
from .base import ApiError, LiteView, clean_text, get_or_404

logger = logging.getLogger(__name__)

MESSAGE_LIMIT = 200


def can_access_room(member, room):
    if member.is_host:
        return True
    if room.kind == ChatRoom.Kind.MEETUP:
        return Rsvp.objects.filter(
            member=member, meetup_id=room.meetup_id, status__in=[Rsvp.Status.GOING, Rsvp.Status.MAYBE]
        ).exists()
    return room.seminar.member_id == member.id


class RoomMessagesView(LiteView):
    def _room(self, room_id):
        room = get_or_404(
            ChatRoom.objects.select_related('seminar'), '채팅방을 찾을 수 없어요', pk=room_id
        )
        if not can_access_room(self.member, room):
            raise ApiError('이 채팅방에 들어갈 수 없어요', 403)
        return room

    def get(self, request, room_id):
        room = self._room(room_id)
        after = request.query_params.get('after')
        qs = ChatMessage.objects.select_related('member').filter(room=room)
        if after not in (None, ''):
            try:
                qs = qs.filter(id__gt=int(after))
            except ValueError:
                raise ApiError('after 값이 올바르지 않아요') from None
        return APIResponse.success({'messages': [message_obj(m) for m in qs.order_by('id')[:MESSAGE_LIMIT]]})

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
