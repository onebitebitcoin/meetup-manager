import logging
import time
from datetime import datetime
from math import ceil

from django.contrib.auth.models import User
from django.db.models import Exists, OuterRef, Q
from django.http import JsonResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..models import Meetup, MeetupUser, Registration, Review, Waitlist
from ..serializers import (
    MeetupSerializer,
    MeetupUserSerializer,
)
from .helpers import (
    APIResponse,
    get_object_or_error,
    get_or_create_meetup_profile,
    require_meetup_access,
    require_meetup_creator,
    require_profile,
)

logger = logging.getLogger(__name__)


class MeetupUserListCreateView(generics.ListCreateAPIView):
    queryset = MeetupUser.objects.all().order_by('-created_at')
    serializer_class = MeetupUserSerializer


@method_decorator(csrf_exempt, name='dispatch')
class MeetupListCreateView(generics.ListCreateAPIView):
    queryset = Meetup.objects.all().order_by('date_time')
    serializer_class = MeetupSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def perform_create(self, serializer):
        if not self.request.user.is_authenticated:
            serializer.save()
            return

        try:
            meetup_user = self.request.user.meetup_profile
            serializer.save(creator=meetup_user)
        except MeetupUser.DoesNotExist:
            serializer.save()


@api_view(['GET', 'PUT', 'DELETE'])
def meetup_detail(request, pk):
    """밋업 상세 조회/수정/삭제"""
    meetup, error = get_object_or_error(Meetup, '모임을 찾을 수 없습니다', pk=pk)
    if error:
        return error

    # GET: 누구나 조회 가능
    if request.method == 'GET':
        serializer = MeetupSerializer(meetup, context={'request': request})
        return Response(serializer.data)

    # PUT/DELETE: 인증 + 생성자/관리자 권한 필요
    if not request.user.is_authenticated:
        return APIResponse.unauthorized()

    try:
        meetup_user = request.user.meetup_profile
    except MeetupUser.DoesNotExist:
        return APIResponse.error('사용자 프로필을 찾을 수 없습니다', status.HTTP_404_NOT_FOUND)

    if meetup.creator != meetup_user and not meetup_user.is_admin:
        return APIResponse.forbidden()

    if request.method == 'PUT':
        serializer = MeetupSerializer(meetup, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE
    meetup.delete()
    return APIResponse.no_content()


@api_view(['GET'])
@require_profile
def user_meetups(request):
    """사용자가 생성한 밋업 목록 조회"""
    meetup_user = request.meetup_user

    month_param = request.query_params.get('month')
    page_param = request.query_params.get('page', 1)
    page_size_param = request.query_params.get('page_size', 10)

    # Determine month range (default = current month)
    tz = timezone.get_current_timezone()
    now = timezone.localtime()
    year = now.year
    month = now.month

    if month_param:
        try:
            parsed_year, parsed_month = month_param.split('-')
            year = int(parsed_year)
            month = int(parsed_month)
            if month < 1 or month > 12:
                raise ValueError
        except (ValueError, AttributeError):
            return APIResponse.error('month 파라미터 형식은 YYYY-MM 이어야 합니다.')

    start_of_month = timezone.make_aware(datetime(year, month, 1, 0, 0, 0), timezone=tz)
    if month == 12:
        end_of_month = timezone.make_aware(datetime(year + 1, 1, 1, 0, 0, 0), timezone=tz)
    else:
        end_of_month = timezone.make_aware(datetime(year, month + 1, 1, 0, 0, 0), timezone=tz)

    queryset = meetup_user.created_meetups.filter(
        date_time__gte=start_of_month,
        date_time__lt=end_of_month,
    ).order_by('-date_time')

    try:
        page = max(1, int(page_param))
    except (TypeError, ValueError):
        page = 1

    try:
        page_size = max(1, min(50, int(page_size_param)))
    except (TypeError, ValueError):
        page_size = 10

    total = queryset.count()
    total_pages = ceil(total / page_size) if total > 0 else 1
    if page > total_pages:
        page = total_pages

    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    current_page_queryset = queryset[start_index:end_index]

    serializer = MeetupSerializer(current_page_queryset, many=True, context={'request': request})
    return Response({
        'data': serializer.data,
        'meta': {
            'page': page,
            'page_size': page_size,
            'total': total,
            'total_pages': total_pages,
            'month': {
                'value': f'{year:04d}-{month:02d}',
            },
        },
    })


def health_check(request):
    return JsonResponse({'status': 'ok', 'message': 'Django 백엔드가 실행 중입니다'})


@api_view(['GET'])
def meetup_registrations(request, meetup_id):
    """밋업 참가자 목록 조회"""
    meetup, error = get_object_or_error(Meetup, '모임을 찾을 수 없습니다', id=meetup_id)
    if error:
        return error

    registrations = Registration.objects.filter(meetup=meetup).select_related('user')
    registration_data = [{
        'id': reg.id,
        'user_name': reg.user.name,
        'user_email': reg.user.email,
        'registered_at': reg.registered_at
    } for reg in registrations]

    return APIResponse.success({'meetup_id': meetup_id, 'registrations': registration_data})


@api_view(['POST'])
@require_meetup_access('meetup_id')
def register_for_meetup(request, meetup_id):
    """밋업 참가 신청"""
    meetup = request.meetup
    meetup_user = request.meetup_user

    if Registration.objects.filter(user=meetup_user, meetup=meetup).exists():
        return APIResponse.error('이미 이 모임에 신청되어 있습니다')

    if Waitlist.objects.filter(user=meetup_user, meetup=meetup).exists():
        return APIResponse.error('이미 이 모임 대기열에 등록되어 있습니다')

    if meetup.is_full:
        return APIResponse.error('모임 정원이 가득 찼습니다')

    registration = Registration.objects.create(user=meetup_user, meetup=meetup)
    return APIResponse.created({
        'message': '신청이 완료되었습니다',
        'registration_id': registration.id
    })


@api_view(['DELETE'])
@require_meetup_access('meetup_id')
def unregister_from_meetup(request, meetup_id):
    """밋업 참가 취소"""
    meetup = request.meetup
    meetup_user = request.meetup_user

    registration, error = get_object_or_error(
        Registration, '신청 정보를 찾을 수 없습니다',
        user=meetup_user, meetup=meetup
    )
    if error:
        return error

    registration.delete()
    return APIResponse.success(message='신청 취소가 완료되었습니다')


@api_view(['GET'])
def check_registration_status(request, meetup_id):
    """밋업 등록 상태 확인"""
    # 비로그인 사용자는 is_registered=False 반환
    if not request.user.is_authenticated:
        return APIResponse.success({'is_registered': False})

    meetup, error = get_object_or_error(Meetup, '모임을 찾을 수 없습니다', id=meetup_id)
    if error:
        return error

    try:
        meetup_user = request.user.meetup_profile
    except MeetupUser.DoesNotExist:
        return APIResponse.success({'is_registered': False})

    is_registered = Registration.objects.filter(user=meetup_user, meetup=meetup).exists()
    return APIResponse.success({'is_registered': is_registered, 'meetup_id': meetup_id})


@api_view(['POST'])
@require_meetup_creator('meetup_id')
def add_participant_by_email(request, meetup_id):
    """이메일로 참가자 추가 (생성자만)"""
    meetup = request.meetup

    email = request.data.get('email')
    if not email:
        return APIResponse.error('이메일이 필요합니다')

    if meetup.is_full:
        return APIResponse.error('모임 정원이 가득 찼습니다')

    # 등록된 사용자만 추가 가능 (없으면 404)
    try:
        django_user = User.objects.get(email=email)
        participant_user = get_or_create_meetup_profile(django_user)
    except User.DoesNotExist:
        try:
            participant_user = MeetupUser.objects.get(email=email, user__isnull=True)
        except MeetupUser.DoesNotExist:
            return APIResponse.not_found('해당 이메일의 사용자를 찾을 수 없습니다')

    if Registration.objects.filter(user=participant_user, meetup=meetup).exists():
        return APIResponse.error('이미 이 모임에 등록된 사용자입니다')

    registration = Registration.objects.create(user=participant_user, meetup=meetup)
    return APIResponse.created({
        'message': '참가자가 성공적으로 추가되었습니다',
        'participant': {
            'id': participant_user.id,
            'name': participant_user.name,
            'email': participant_user.email,
            'registration_id': registration.id
        }
    })


@api_view(['DELETE'])
@require_meetup_creator('meetup_id')
def remove_participant(request, meetup_id, registration_id):
    """참가자 제거 (생성자만)"""
    meetup = request.meetup

    registration, error = get_object_or_error(
        Registration, '신청 정보를 찾을 수 없습니다',
        id=registration_id, meetup=meetup
    )
    if error:
        return error

    registration.delete()
    return APIResponse.success(message='참가자가 성공적으로 제거되었습니다')


def _resolve_participant(email):
    """
    이메일로 참가자 조회 또는 게스트 프로필 생성
    """
    try:
        django_user = User.objects.get(email=email)
        return get_or_create_meetup_profile(django_user)
    except User.DoesNotExist:
        try:
            return MeetupUser.objects.get(email=email, user__isnull=True)
        except MeetupUser.DoesNotExist:
            return MeetupUser.objects.create(name=f"Guest ({email})", email=email, is_admin=False)


@api_view(['GET'])
@require_profile
def user_attended_meetups(request):
    """
    사용자가 참가한 밋업 중 종료된 밋업 목록 조회
    후기 작성 여부(has_review) 포함
    """
    started_at = time.perf_counter()
    meetup_user = request.meetup_user
    now = timezone.now()

    # 참가/생성 조건과 종료 조건을 DB 레벨에서 처리하여 Python 후처리를 최소화한다.
    meetups = Meetup.objects.filter(
        Q(registration__user=meetup_user) | Q(creator=meetup_user)
    ).filter(
        Q(end_time__lt=now) | Q(end_time__isnull=True, date_time__lt=now)
    ).annotate(
        has_review=Exists(
            Review.objects.filter(
                meetup=OuterRef('pk'),
                user=meetup_user
            )
        )
    ).order_by('-date_time').distinct()

    ended_meetups = []
    for meetup in meetups:
        ended_meetups.append({
            'id': meetup.id,
            'name': meetup.name,
            'date_time': meetup.date_time.isoformat(),
            'end_time': meetup.end_time.isoformat() if meetup.end_time else None,
            'location': meetup.location,
            'image_display_url': meetup.image.url if meetup.image else None,
            'has_review': meetup.has_review,
        })

    duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
    logger.info(
        "user_attended_meetups user=%s total=%s duration_ms=%s",
        meetup_user.id,
        len(ended_meetups),
        duration_ms,
    )

    return APIResponse.success({
        'meetups': ended_meetups,
        'total': len(ended_meetups)
    })
