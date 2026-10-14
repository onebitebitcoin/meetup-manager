import logging
import secrets

from django.conf import settings
from django.db import IntegrityError
from rest_framework.permissions import AllowAny
from rest_framework.throttling import AnonRateThrottle

from meetups.views.helpers import APIResponse

from ..models import Member
from ..serializers import member_full
from .base import ApiError, LiteView, clean_text

logger = logging.getLogger(__name__)


class MemberCreateThrottle(AnonRateThrottle):
    scope = 'lite_member_create'
    rate = '10/hour'


class MemberCreateView(LiteView):
    permission_classes = [AllowAny]
    throttle_classes = [MemberCreateThrottle]

    def post(self, request):
        name = clean_text(self.json_body().get('name'), '이름', 1, 20)
        if Member.objects.filter(name=name).exists():
            raise ApiError('이미 사용 중인 이름이에요', 409)
        try:
            member = Member.objects.create(name=name)
        except IntegrityError:
            raise ApiError('이미 사용 중인 이름이에요', 409) from None
        logger.info('LITE 회원 생성: id=%s name=%s', member.id, member.name)
        return APIResponse.created({'token': member.token, 'member': member_full(member)})


class MeView(LiteView):
    def get(self, request):
        return APIResponse.success({'member': member_full(self.member)})


class HostClaimView(LiteView):
    def post(self, request):
        key = self.json_body().get('key')
        host_key = settings.LITE_HOST_KEY
        if not host_key or not isinstance(key, str) or not secrets.compare_digest(key.encode(), host_key.encode()):
            logger.warning('LITE 운영자 승격 실패: member_id=%s', self.member.id)
            raise ApiError('운영자 키가 맞지 않아요', 403)
        member = self.member
        if not member.is_host:
            member.is_host = True
            member.save(update_fields=['is_host'])
            logger.info('LITE 운영자 승격: member_id=%s', member.id)
        return APIResponse.success({'member': member_full(member)})
