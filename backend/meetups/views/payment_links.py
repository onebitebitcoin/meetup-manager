import logging
from datetime import timedelta

from django.utils import timezone
from rest_framework.decorators import api_view

from ..models import MeetupPaymentLink
from ..views.auth import LightningServiceError, create_one_sat_invoice
from .helpers import APIResponse, require_meetup_creator

logger = logging.getLogger(__name__)


@api_view(['POST'])
@require_meetup_creator('meetup_id')
def create_meetup_payment_link(request, meetup_id):
    """모임 결제 링크 생성 (생성자 전용) - 1 sats BOLT11 인보이스를 공개 URL로 공유"""
    meetup_user = request.meetup_user

    if not meetup_user.lightning_address:
        return APIResponse.error('라이트닝 주소를 먼저 설정해주세요. (설정 페이지에서 등록)')

    try:
        result = create_one_sat_invoice(meetup_user.lightning_address)
    except LightningServiceError as exc:
        logger.warning(
            'Payment link creation failed meetup_id=%s user=%s error=%s',
            meetup_id, meetup_user.id, exc,
        )
        return APIResponse.error(str(exc), exc.status_code)

    expires_at = timezone.now() + timedelta(hours=1)
    payment_link = MeetupPaymentLink.objects.create(
        meetup=request.meetup,
        bolt11=result['invoice'],
        expires_at=expires_at,
    )

    logger.info('Payment link created meetup_id=%s token=%s', meetup_id, payment_link.token)
    return APIResponse.created({
        'token': str(payment_link.token),
        'bolt11': result['invoice'],
        'expires_at': payment_link.expires_at.isoformat(),
    })


@api_view(['GET'])
def get_payment_link(request, token):
    """결제 링크 조회 (공개, 인증 불필요)"""
    try:
        payment_link = MeetupPaymentLink.objects.select_related('meetup').get(token=token)
    except (MeetupPaymentLink.DoesNotExist, ValueError):
        return APIResponse.not_found('결제 링크를 찾을 수 없습니다.')

    return APIResponse.success({
        'bolt11': payment_link.bolt11,
        'meetup_name': payment_link.meetup.name,
        'expires_at': payment_link.expires_at.isoformat(),
        'is_expired': payment_link.is_expired,
    })
