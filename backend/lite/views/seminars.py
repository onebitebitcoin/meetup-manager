import logging

from django.db import transaction

from meetups.views.helpers import APIResponse

from ..auth import IsHost
from ..models import ChatMessage, ChatRoom, LiteConfig, SeminarRequest
from ..serializers import seminar_card
from .base import ApiError, LiteView, get_or_404

logger = logging.getLogger(__name__)

MODE_LABELS = {SeminarRequest.Mode.ONLINE: '온라인', SeminarRequest.Mode.OFFLINE: '오프라인'}


def guide(room, body):
    return ChatMessage.objects.create(room=room, kind=ChatMessage.Kind.GUIDE, body=body)


def seminar_qs():
    return SeminarRequest.objects.select_related('member', 'room')


class SeminarView(LiteView):
    def post(self, request):
        member = self.member
        with transaction.atomic():
            seminar, created = SeminarRequest.objects.get_or_create(member=member)
            if created:
                room = ChatRoom.objects.create(kind=ChatRoom.Kind.SEMINAR, seminar=seminar)
                config = LiteConfig.get()
                guide(room, config.seminar_guide_1)
                guide(room, config.seminar_guide_2)
                logger.info('LITE 세미나 시작: seminar_id=%s member_id=%s', seminar.id, member.id)
        return APIResponse.success({'seminar': seminar_card(seminar_qs().get(pk=seminar.pk))})


class SeminarModeView(LiteView):
    def post(self, request):
        member = self.member
        mode = self.json_body().get('mode')
        if mode not in MODE_LABELS:
            raise ApiError('진행 방식은 online 또는 offline이어야 해요')
        with transaction.atomic():
            seminar = get_or_404(
                seminar_qs().select_for_update(of=('self',)), '세미나를 먼저 시작해 주세요', member=member
            )
            if seminar.status != SeminarRequest.Status.GUIDE:
                raise ApiError('이미 접수된 세미나예요')
            seminar.mode = mode
            seminar.save(update_fields=['mode'])
            ChatMessage.objects.create(
                room=seminar.room, member=member, kind=ChatMessage.Kind.USER, body=MODE_LABELS[mode]
            )
            guide(seminar.room, LiteConfig.get().seminar_guide_3)
        return APIResponse.success({'seminar': seminar_card(seminar)})


class SeminarConfirmView(LiteView):
    permission_classes = [IsHost]

    def post(self, request, seminar_id):
        with transaction.atomic():
            seminar = get_or_404(seminar_qs().select_for_update(of=('self',)), '세미나를 찾을 수 없어요', pk=seminar_id)
            if seminar.status != SeminarRequest.Status.CONFIRMED:
                seminar.status = SeminarRequest.Status.CONFIRMED
                seminar.save(update_fields=['status'])
                ChatMessage.objects.create(room=seminar.room, kind=ChatMessage.Kind.SYSTEM, body='일정 확정')
                logger.info('LITE 세미나 확정: seminar_id=%s', seminar.id)
        return APIResponse.success({'seminar': seminar_card(seminar)})
