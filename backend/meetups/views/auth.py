import json
import logging
import os
import re
import time
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse
from urllib.request import Request, urlopen

from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from ..serializers import UserRegistrationSerializer
from ..utils.keyboard_converter import has_korean_characters, korean_to_english
from ..utils.secure_logging import log_korean_conversion
from .helpers import get_or_create_meetup_profile

logger = logging.getLogger(__name__)

LIGHTNING_USERNAME_PATTERN = re.compile(r'^[A-Za-z0-9._+-]+$')
LIGHTNING_DOMAIN_PATTERN = re.compile(
    r'^(?=.{1,253}$)(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+[A-Za-z]{2,63}$'
)
ONE_SAT_MSAT = 1000


class LightningServiceError(Exception):
    def __init__(self, message, status_code=status.HTTP_400_BAD_REQUEST):
        super().__init__(message)
        self.status_code = status_code


def normalize_lightning_address(raw_address):
    address = (raw_address or '').strip()
    if not address:
        raise LightningServiceError('라이트닝 주소를 입력해주세요.')

    if address.startswith('@'):
        address = address[1:]

    if address.count('@') != 1:
        raise LightningServiceError('라이트닝 주소 형식이 올바르지 않습니다. (예: user@coinos.io)')

    username, domain = address.split('@', 1)
    username = username.strip()
    domain = domain.strip().lower()

    if not username or not domain:
        raise LightningServiceError('라이트닝 주소 형식이 올바르지 않습니다. (예: user@coinos.io)')

    if not LIGHTNING_USERNAME_PATTERN.match(username):
        raise LightningServiceError('라이트닝 사용자명 형식이 올바르지 않습니다.')

    if not LIGHTNING_DOMAIN_PATTERN.match(domain):
        raise LightningServiceError('라이트닝 도메인 형식이 올바르지 않습니다.')

    return f'{username}@{domain}'


def _get_lightning_timeout():
    try:
        return max(1.0, float(os.environ.get('LIGHTNING_HTTP_TIMEOUT_SEC', '5')))
    except ValueError:
        return 5.0


def _get_lightning_user_agent():
    return os.environ.get('LIGHTNING_HTTP_USER_AGENT', 'meetup-manager-lightning-checker/1.0')


def fetch_json_with_timeout(url):
    timeout = _get_lightning_timeout()
    user_agent = _get_lightning_user_agent()
    request = Request(url, headers={
        'Accept': 'application/json',
        'User-Agent': user_agent,
    })
    start_time = time.monotonic()

    try:
        with urlopen(request, timeout=timeout) as response:  # nosec B310 - trusted LNURL endpoints from user input
            raw_body = response.read().decode('utf-8')
            status_code = response.getcode()
    except HTTPError as exc:
        error_body = exc.read().decode('utf-8', errors='ignore')
        logger.warning('Lightning HTTP error url=%s status=%s body=%s', url, exc.code, error_body[:300])
        raise LightningServiceError(
            f'라이트닝 서버 응답 오류가 발생했습니다. (HTTP {exc.code})',
            status.HTTP_502_BAD_GATEWAY,
        ) from exc
    except (URLError, TimeoutError) as exc:
        logger.warning('Lightning network error url=%s error=%s', url, exc)
        raise LightningServiceError(
            '라이트닝 서버 연결에 실패했습니다. 잠시 후 다시 시도해주세요.',
            status.HTTP_504_GATEWAY_TIMEOUT,
        ) from exc
    except Exception as exc:
        logger.exception('Unexpected lightning fetch error url=%s', url)
        raise LightningServiceError(
            '라이트닝 서버 호출 중 알 수 없는 오류가 발생했습니다.',
            status.HTTP_502_BAD_GATEWAY,
        ) from exc

    elapsed_ms = (time.monotonic() - start_time) * 1000
    logger.info('Lightning fetch success url=%s status=%s elapsed_ms=%.2f', url, status_code, elapsed_ms)

    try:
        return json.loads(raw_body)
    except json.JSONDecodeError as exc:
        logger.warning('Lightning invalid JSON url=%s body=%s', url, raw_body[:300])
        raise LightningServiceError(
            '라이트닝 서버가 올바른 JSON을 반환하지 않았습니다.',
            status.HTTP_502_BAD_GATEWAY,
        ) from exc


def _append_amount(callback_url, amount_msat):
    parsed = urlparse(callback_url)
    query_pairs = parse_qsl(parsed.query, keep_blank_values=True)
    query_pairs = [(k, v) for k, v in query_pairs if k != 'amount']
    query_pairs.append(('amount', str(amount_msat)))
    return urlunparse(parsed._replace(query=urlencode(query_pairs)))


def create_one_sat_invoice(lightning_address):
    username, domain = lightning_address.split('@', 1)
    lnurlp_url = f'https://{domain}/.well-known/lnurlp/{username}'

    lnurl_data = fetch_json_with_timeout(lnurlp_url)
    if lnurl_data.get('status') == 'ERROR':
        reason = lnurl_data.get('reason') or 'LNURL 조회가 실패했습니다.'
        raise LightningServiceError(reason)

    if lnurl_data.get('tag') != 'payRequest':
        raise LightningServiceError('지원되지 않는 LNURL 응답입니다. (payRequest 필요)')

    callback_url = lnurl_data.get('callback')
    if not callback_url:
        raise LightningServiceError('LNURL callback 정보를 찾을 수 없습니다.')

    min_sendable = int(lnurl_data.get('minSendable') or 0)
    max_sendable = int(lnurl_data.get('maxSendable') or 0)

    if min_sendable > ONE_SAT_MSAT or max_sendable < ONE_SAT_MSAT:
        raise LightningServiceError(
            f'해당 서비스는 1 sats 인보이스를 지원하지 않습니다. (min={min_sendable}, max={max_sendable})'
        )

    callback_with_amount = _append_amount(callback_url, ONE_SAT_MSAT)
    callback_data = fetch_json_with_timeout(callback_with_amount)

    if callback_data.get('status') == 'ERROR':
        reason = callback_data.get('reason') or '인보이스 생성에 실패했습니다.'
        raise LightningServiceError(reason)

    invoice = callback_data.get('pr')
    if not invoice:
        raise LightningServiceError('인보이스 응답에 BOLT11(pr)이 없습니다.')

    return {
        'lnurlp_url': lnurlp_url,
        'callback_url': callback_with_amount,
        'invoice': invoice,
    }


@csrf_exempt
@ensure_csrf_cookie
def get_csrf_token(request):
    token = get_token(request)
    print(f"CSRF token requested: {token[:10]}...")
    print(f"Request origin: {request.META.get('HTTP_ORIGIN')}")
    print(f"Request referer: {request.META.get('HTTP_REFERER')}")
    return JsonResponse({'csrfToken': token})


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def check_username_availability(request):
    username = request.GET.get('username')
    if not username:
        return Response({'error': '사용자명이 필요합니다'}, status=status.HTTP_400_BAD_REQUEST)

    exists = User.objects.filter(username__iexact=username).exists()
    return Response({'available': not exists, 'username': username}, status=status.HTTP_200_OK)


@api_view(['POST'])
@csrf_exempt
def register_new_user(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = serializer.save()
        login(request, user)
        meetup_user = get_or_create_meetup_profile(user)
        return Response({
            'message': '계정이 성공적으로 생성되었습니다',
            'user': {
                'id': meetup_user.id,
                'username': user.username,
                'name': meetup_user.name,
                'email': user.email,
                'is_admin': meetup_user.is_admin or user.is_staff,
                'lightning_address': meetup_user.lightning_address or '',
            }
        }, status=status.HTTP_201_CREATED)
    except IntegrityError:
        return Response({'error': '사용자명 또는 이메일이 이미 존재합니다'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@csrf_exempt
def login_user(request):
    print(f"Login attempt for user: {request.data.get('username')}")
    print(f"Request method: {request.method}")
    print(f"Request origin: {request.META.get('HTTP_ORIGIN')}")
    print(f"Request referer: {request.META.get('HTTP_REFERER')}")
    print(f"CSRF token in header: {request.META.get('HTTP_X_CSRFTOKEN', 'None')[:10]}...")

    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({'error': '사용자명과 비밀번호가 필요합니다'}, status=status.HTTP_400_BAD_REQUEST)

    if has_korean_characters(password):
        password = korean_to_english(password)
        log_korean_conversion(username, action="login")

    user = authenticate(username=username, password=password)
    username_exists = User.objects.filter(username=username).exists()

    if not user and '@' in username:
        django_users = User.objects.filter(email=username)
        if django_users.exists():
            username_exists = True
            for django_user in django_users:
                user = authenticate(username=django_user.username, password=password)
                if user:
                    break

    if not user:
        if not username_exists:
            return Response({
                'error': 'ID/사용자명이 존재하지 않습니다',
                'contact': 'onebitebitcoin@proton.me'
            }, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({
                'error': '비밀번호를 확인하세요'
            }, status=status.HTTP_401_UNAUTHORIZED)

    login(request, user)
    meetup_user = get_or_create_meetup_profile(user)

    return Response({
        'message': '로그인 성공',
        'user': {
            'id': meetup_user.id,
            'username': user.username,
            'name': meetup_user.name,
            'email': user.email,
            'is_admin': meetup_user.is_admin or user.is_staff,
            'lightning_address': meetup_user.lightning_address or '',
        }
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
def logout_user(request):
    logout(request)
    return Response({'message': '로그아웃 성공'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@csrf_exempt
def change_password(request):
    if not request.user.is_authenticated:
        return Response({'error': '로그인이 필요합니다'}, status=status.HTTP_401_UNAUTHORIZED)

    current_password = request.data.get('current_password')
    new_password = request.data.get('new_password')

    if not current_password or not new_password:
        return Response({'error': '현재 비밀번호와 새 비밀번호가 필요합니다'}, status=status.HTTP_400_BAD_REQUEST)

    # 한글 키보드 자동 변환 지원
    if has_korean_characters(current_password):
        current_password = korean_to_english(current_password)
        log_korean_conversion(request.user.username, action="change_password_current")

    if has_korean_characters(new_password):
        new_password = korean_to_english(new_password)
        log_korean_conversion(request.user.username, action="change_password_new")

    # 현재 비밀번호 검증
    if not request.user.check_password(current_password):
        return Response({'error': '현재 비밀번호가 틀렸습니다'}, status=status.HTTP_400_BAD_REQUEST)

    # 새 비밀번호 validation
    if len(new_password) < 8:
        return Response({'error': '새 비밀번호는 최소 8자 이상이어야 합니다'}, status=status.HTTP_400_BAD_REQUEST)

    # 현재 비밀번호와 새 비밀번호 동일 여부 확인
    if current_password == new_password:
        return Response({'error': '새 비밀번호는 현재 비밀번호와 달라야 합니다'}, status=status.HTTP_400_BAD_REQUEST)

    # 비밀번호 변경
    request.user.set_password(new_password)
    request.user.save()

    # 세션 유지
    update_session_auth_hash(request, request.user)

    return Response({'message': '비밀번호가 성공적으로 변경되었습니다'}, status=status.HTTP_200_OK)


@api_view(['GET', 'PUT'])
def lightning_address(request):
    if not request.user.is_authenticated:
        return Response({'error': '로그인이 필요합니다'}, status=status.HTTP_401_UNAUTHORIZED)

    meetup_user = get_or_create_meetup_profile(request.user)

    if request.method == 'GET':
        return Response({
            'lightning_address': meetup_user.lightning_address or '',
        }, status=status.HTTP_200_OK)

    raw_address = request.data.get('lightning_address')
    if raw_address is None:
        return Response({'error': 'lightning_address 필드가 필요합니다'}, status=status.HTTP_400_BAD_REQUEST)

    raw_address = str(raw_address).strip()

    if not raw_address:
        meetup_user.lightning_address = ''
        meetup_user.save(update_fields=['lightning_address'])
        logger.info('Lightning address cleared username=%s', request.user.username)
        return Response({
            'message': '라이트닝 주소가 삭제되었습니다.',
            'lightning_address': '',
        }, status=status.HTTP_200_OK)

    try:
        normalized_address = normalize_lightning_address(raw_address)
    except LightningServiceError as exc:
        return Response({'error': str(exc)}, status=exc.status_code)

    meetup_user.lightning_address = normalized_address
    meetup_user.save(update_fields=['lightning_address'])
    logger.info('Lightning address saved username=%s address=%s', request.user.username, normalized_address)

    return Response({
        'message': '라이트닝 주소가 저장되었습니다.',
        'lightning_address': normalized_address,
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
def test_lightning_invoice(request):
    if not request.user.is_authenticated:
        return Response({'error': '로그인이 필요합니다'}, status=status.HTTP_401_UNAUTHORIZED)

    meetup_user = get_or_create_meetup_profile(request.user)
    raw_address = request.data.get('lightning_address')

    if raw_address is None or not str(raw_address).strip():
        raw_address = meetup_user.lightning_address

    if not raw_address:
        return Response({
            'error': '먼저 라이트닝 주소를 저장하거나 테스트할 주소를 입력해주세요.',
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        normalized_address = normalize_lightning_address(raw_address)
        result = create_one_sat_invoice(normalized_address)
    except LightningServiceError as exc:
        logger.warning('Lightning invoice test failed username=%s error=%s', request.user.username, exc)
        return Response({
            'error': str(exc),
            'lightning_address': str(raw_address).strip(),
        }, status=exc.status_code)

    logger.info('Lightning invoice test success username=%s address=%s', request.user.username, normalized_address)
    return Response({
        'message': '1 sats 인보이스 생성에 성공했습니다.',
        'lightning_address': normalized_address,
        'lnurlp_url': result['lnurlp_url'],
        'callback_url': result['callback_url'],
        'invoice': {
            'amount_sats': 1,
            'bolt11': result['invoice'],
        },
    }, status=status.HTTP_200_OK)
