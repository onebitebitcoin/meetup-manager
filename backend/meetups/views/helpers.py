from datetime import datetime

from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response

from ..models import Meetup, MeetupUser


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
