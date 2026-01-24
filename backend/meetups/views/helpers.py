from datetime import datetime
from functools import wraps

from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response

from ..models import Meetup, MeetupUser, Registration


# =============================================================================
# APIResponse: 일관된 응답 생성 클래스
# =============================================================================

class APIResponse:
    """일관된 API 응답 생성 클래스"""

    @staticmethod
    def success(data=None, message=None, status_code=status.HTTP_200_OK):
        """성공 응답"""
        response_data = {}
        if data is not None:
            if isinstance(data, dict):
                response_data.update(data)
            else:
                response_data['data'] = data
        if message:
            response_data['message'] = message
        return Response(response_data, status=status_code)

    @staticmethod
    def created(data=None, message=None):
        """생성 성공 응답"""
        return APIResponse.success(data, message, status.HTTP_201_CREATED)

    @staticmethod
    def no_content():
        """내용 없음 응답 (삭제 성공 등)"""
        return Response(status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def error(message, status_code=status.HTTP_400_BAD_REQUEST):
        """에러 응답"""
        return Response({'error': message}, status=status_code)

    @staticmethod
    def not_found(message='찾을 수 없습니다'):
        """404 응답"""
        return Response({'error': message}, status=status.HTTP_404_NOT_FOUND)

    @staticmethod
    def forbidden(message='권한이 없습니다'):
        """403 응답"""
        return Response({'error': message}, status=status.HTTP_403_FORBIDDEN)

    @staticmethod
    def unauthorized(message='로그인이 필요합니다'):
        """401 응답"""
        return Response({'error': message}, status=status.HTTP_401_UNAUTHORIZED)


# =============================================================================
# 제네릭 모델 접근 헬퍼
# =============================================================================

def get_object_or_error(model, error_msg=None, **kwargs):
    """
    모델 객체 조회, 없으면 (None, error_response) 반환
    Returns (object, None) on success, (None, Response) on failure
    """
    default_msg = '찾을 수 없습니다'
    try:
        return model.objects.get(**kwargs), None
    except model.DoesNotExist:
        return None, APIResponse.not_found(error_msg or default_msg)


# =============================================================================
# 데코레이터: 인증 및 권한 검증
# =============================================================================

def require_auth(view_func):
    """로그인 필수 데코레이터"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return APIResponse.unauthorized()
        return view_func(request, *args, **kwargs)
    return wrapper


def require_profile(view_func):
    """MeetupUser 프로필 필수 데코레이터 (require_auth 포함)"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return APIResponse.unauthorized()
        try:
            request.meetup_user = request.user.meetup_profile
        except MeetupUser.DoesNotExist:
            return APIResponse.error('사용자 프로필을 찾을 수 없습니다', status.HTTP_404_NOT_FOUND)
        return view_func(request, *args, **kwargs)
    return wrapper


def require_meetup_access(param_name='meetup_id'):
    """
    밋업 존재 확인 + 접근 권한 데코레이터
    request.meetup에 밋업 객체 주입
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return APIResponse.unauthorized()
            try:
                request.meetup_user = request.user.meetup_profile
            except MeetupUser.DoesNotExist:
                return APIResponse.error('사용자 프로필을 찾을 수 없습니다', status.HTTP_404_NOT_FOUND)

            meetup_id = kwargs.get(param_name)
            meetup, error = get_object_or_error(Meetup, '모임을 찾을 수 없습니다', id=meetup_id)
            if error:
                return error
            request.meetup = meetup
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def require_meetup_creator(param_name='meetup_id'):
    """밋업 생성자만 허용 데코레이터"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return APIResponse.unauthorized()
            try:
                request.meetup_user = request.user.meetup_profile
            except MeetupUser.DoesNotExist:
                return APIResponse.error('사용자 프로필을 찾을 수 없습니다', status.HTTP_404_NOT_FOUND)

            meetup_id = kwargs.get(param_name)
            meetup, error = get_object_or_error(Meetup, '모임을 찾을 수 없습니다', id=meetup_id)
            if error:
                return error
            request.meetup = meetup

            if meetup.creator != request.meetup_user:
                return APIResponse.forbidden('모임 생성자만 접근할 수 있습니다')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def require_meetup_creator_or_admin(param_name='meetup_id'):
    """밋업 생성자 또는 관리자만 허용 데코레이터"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return APIResponse.unauthorized()
            try:
                request.meetup_user = request.user.meetup_profile
            except MeetupUser.DoesNotExist:
                return APIResponse.error('사용자 프로필을 찾을 수 없습니다', status.HTTP_404_NOT_FOUND)

            meetup_id = kwargs.get(param_name)
            meetup, error = get_object_or_error(Meetup, '모임을 찾을 수 없습니다', id=meetup_id)
            if error:
                return error
            request.meetup = meetup

            if meetup.creator != request.meetup_user and not request.meetup_user.is_admin:
                return APIResponse.forbidden()
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def require_meetup_participant(param_name='meetup_id'):
    """밋업 참가자만 허용 데코레이터"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return APIResponse.unauthorized()
            try:
                request.meetup_user = request.user.meetup_profile
            except MeetupUser.DoesNotExist:
                return APIResponse.error('사용자 프로필을 찾을 수 없습니다', status.HTTP_404_NOT_FOUND)

            meetup_id = kwargs.get(param_name)
            meetup, error = get_object_or_error(Meetup, '모임을 찾을 수 없습니다', id=meetup_id)
            if error:
                return error
            request.meetup = meetup

            if not Registration.objects.filter(meetup=meetup, user=request.meetup_user).exists():
                return APIResponse.forbidden('모임 참가자만 접근할 수 있습니다')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def require_meetup_creator_or_participant(param_name='meetup_id'):
    """밋업 생성자 또는 참가자만 허용 데코레이터"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return APIResponse.unauthorized()
            try:
                request.meetup_user = request.user.meetup_profile
            except MeetupUser.DoesNotExist:
                return APIResponse.error('사용자 프로필을 찾을 수 없습니다', status.HTTP_404_NOT_FOUND)

            meetup_id = kwargs.get(param_name)
            meetup, error = get_object_or_error(Meetup, '모임을 찾을 수 없습니다', id=meetup_id)
            if error:
                return error
            request.meetup = meetup

            is_creator = meetup.creator == request.meetup_user
            is_participant = Registration.objects.filter(meetup=meetup, user=request.meetup_user).exists()
            if not is_creator and not is_participant:
                return APIResponse.forbidden('모임 참가자 또는 생성자만 접근할 수 있습니다')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def require_admin(view_func):
    """관리자만 허용 데코레이터"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return APIResponse.unauthorized()
        try:
            meetup_user = request.user.meetup_profile
            is_admin = request.user.is_staff or meetup_user.is_admin
        except MeetupUser.DoesNotExist:
            is_admin = request.user.is_staff
        if not is_admin:
            return APIResponse.forbidden('관리자 권한이 필요합니다')
        return view_func(request, *args, **kwargs)
    return wrapper


# =============================================================================
# 기존 헬퍼 함수 (하위 호환성 유지)
# =============================================================================


def parse_datetime_iso(datetime_str):
    """
    ISO 형식 문자열을 datetime 객체로 파싱.
    'Z' 접미사를 '+00:00'으로 변환하여 Python 3.10 이하에서도 호환.
    Returns (datetime, error_response) tuple.
    """
    if not datetime_str:
        return None, Response({'error': '날짜/시간을 입력해주세요'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        # Handle ISO format with 'Z' suffix (Python 3.10 이하 호환)
        if datetime_str.endswith('Z'):
            datetime_str = datetime_str[:-1] + '+00:00'
        dt = datetime.fromisoformat(datetime_str)
        # Make timezone aware if naive
        if dt.tzinfo is None:
            dt = timezone.make_aware(dt)
        return dt, None
    except ValueError:
        return None, Response({'error': '날짜/시간 형식이 올바르지 않습니다'}, status=status.HTTP_400_BAD_REQUEST)


def ensure_authenticated(request, error_body=None, status_code=status.HTTP_401_UNAUTHORIZED):
    """
    Ensure the incoming request is from an authenticated user.
    Returns a Response when authentication fails so callers can return early.
    """
    if request.user.is_authenticated:
        return None
    body = error_body or {'error': '로그인이 필요합니다'}
    return Response(body, status=status_code)


def get_meetup_user_or_response(request, not_found_body=None, not_found_status=status.HTTP_404_NOT_FOUND):
    """
    Fetch the MeetupUser profile linked to the requesting user.
    Returns a (meetup_user, error_response) tuple where error_response is populated on failure.
    """
    try:
        return request.user.meetup_profile, None
    except MeetupUser.DoesNotExist:
        body = not_found_body or {'error': '사용자 프로필을 찾을 수 없습니다'}
        return None, Response(body, status=not_found_status)


def get_meetup_or_response(identifier, lookup_field='id', message='모임을 찾을 수 없습니다'):
    """
    Retrieve a Meetup instance by a specific lookup field.
    Returns (meetup, error_response).
    """
    try:
        return Meetup.objects.get(**{lookup_field: identifier}), None
    except Meetup.DoesNotExist:
        return None, Response({'error': message}, status=status.HTTP_404_NOT_FOUND)


def ensure_meetup_creator_or_admin(meetup, meetup_user, message='권한이 없습니다'):
    """
    Verify the meetup_user either created the meetup or has admin privileges.
    """
    if meetup.creator == meetup_user or meetup_user.is_admin:
        return None
    return Response({'error': message}, status=status.HTTP_403_FORBIDDEN)


def ensure_meetup_creator(meetup, meetup_user, message='모임 생성자만 접근할 수 있습니다'):
    """
    Verify the meetup_user created the meetup.
    """
    if meetup.creator == meetup_user:
        return None
    return Response({'error': message}, status=status.HTTP_403_FORBIDDEN)


def get_or_create_meetup_profile(user: User):
    """
    Ensure a MeetupUser profile exists for the given Django user.
    """
    try:
        return user.meetup_profile
    except MeetupUser.DoesNotExist:
        return MeetupUser.objects.create(
            user=user,
            name=user.username,
            email=user.email,
            is_admin=user.is_staff
        )
