import logging

from django.db import transaction

from meetups.views.helpers import APIResponse

from ..auth import IsHost, IsMember, IsOpenOrHost
from ..models import ChatMessage, LiteConfig, SeminarRequest
from ..serializers import seminar_card
from ..services import seminars_with_last_message
from .base import LiteView, get_or_404

logger = logging.getLogger(__name__)


def guide(room, body):
    return ChatMessage.objects.create(room=room, kind=ChatMessage.Kind.GUIDE, body=body)


class SeminarView(LiteView):
    permission_classes = [IsMember, IsOpenOrHost]
    def post(self, request):
        member = self.member
        with transaction.atomic():
            seminar, created = SeminarRequest.objects.get_or_create(member=member)
            if created:
                room = seminar.room
                config = LiteConfig.get()
                guide(room, config.seminar_guide_1)
                guide(room, config.seminar_guide_2)
                guide(room, config.seminar_guide_3)
                logger.info('LITE 세미나 시작: seminar_id=%s member_id=%s', seminar.id, member.id)
        return APIResponse.success({'seminar': seminar_card(seminars_with_last_message().get(pk=seminar.pk))})


class SeminarConfirmView(LiteView):
    permission_classes = [IsHost]

    def post(self, request, seminar_id):
        with transaction.atomic():
            seminar = get_or_404(seminars_with_last_message().select_for_update(of=('self',)), '세미나를 찾을 수 없어요', pk=seminar_id)
            if seminar.status != SeminarRequest.Status.CONFIRMED:
                seminar.status = SeminarRequest.Status.CONFIRMED
                seminar.save(update_fields=['status'])
                ChatMessage.objects.create(room=seminar.room, kind=ChatMessage.Kind.SYSTEM, body='일정 확정')
                logger.info('LITE 세미나 확정: seminar_id=%s', seminar.id)
        return APIResponse.success({'seminar': seminar_card(seminars_with_last_message().get(pk=seminar.pk))})
