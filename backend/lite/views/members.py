import logging
import secrets
import unicodedata

from django.conf import settings
from django.db import IntegrityError
from rest_framework.permissions import AllowAny

from meetups.views.helpers import APIResponse

from ..models import Member
from ..serializers import member_full
from ..throttles import HostClaimThrottle, MemberCreateThrottle
from .base import ApiError, LiteView, clean_text

logger = logging.getLogger(__name__)


RESERVED_NAMES = frozenset({'운영자', '관리자', 'admin', 'host'})


def clean_name(value):
    """NFKC 정규화 후 길이·문자 종류·예약어를 검증한다."""
    if not isinstance(value, str):
        raise ApiError('이름을 입력해 주세요')
    name = clean_text(unicodedata.normalize('NFKC', value), '이름', 1, 20)
    # C*(제어문자·제로폭 등 Cf 포함), Zl/Zp(줄·문단 구분자)
    if any(unicodedata.category(ch)[0] == 'C' or unicodedata.category(ch) in ('Zl', 'Zp') for ch in name):
        raise ApiError('이름에 쓸 수 없는 문자가 들어 있어요')
    if ''.join(name.split()).casefold() in RESERVED_NAMES:
        raise ApiError('사용할 수 없는 이름이에요')
    return name


class MemberCreateView(LiteView):
    permission_classes = [AllowAny]
    throttle_classes = [MemberCreateThrottle]

    def post(self, request):
        name = clean_name(self.json_body().get('name'))
        if Member.objects.filter(name=name).exists():
            raise ApiError('이미 사용 중인 이름이에요', 409)
        try:
            member = Member.objects.create(name=name)
        except IntegrityError:
            raise ApiError('이미 사용 중인 이름이에요', 409) from None
        logger.info('LITE 회원 생성: id=%s', member.id)
        return APIResponse.created({'token': member.token, 'member': member_full(member)})


class MeView(LiteView):
    def get(self, request):
        return APIResponse.success({'member': member_full(self.member)})


class HostClaimView(LiteView):
    throttle_classes = [HostClaimThrottle]

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
