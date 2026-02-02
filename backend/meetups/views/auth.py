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
                'is_admin': meetup_user.is_admin or user.is_staff
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
            'is_admin': meetup_user.is_admin or user.is_staff
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
