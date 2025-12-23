from datetime import datetime
from math import ceil

from django.contrib.auth.models import User
from django.http import JsonResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..models import MeetupUser, Meetup, Registration, Waitlist
from ..serializers import (
    MeetupUserSerializer,
    MeetupSerializer,
)
from .helpers import (
    ensure_authenticated,
    ensure_meetup_creator,
    ensure_meetup_creator_or_admin,
    get_meetup_or_response,
    get_meetup_user_or_response,
    get_or_create_meetup_profile,
)


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

        meetup_user, error = get_meetup_user_or_response(self.request)
        if error:
            serializer.save()
            return

        serializer.save(creator=meetup_user)


@api_view(['GET', 'PUT', 'DELETE'])
def meetup_detail(request, pk):
    meetup, error = get_meetup_or_response(pk, lookup_field='pk')
    if error:
        return error

    if request.method == 'GET':
        serializer = MeetupSerializer(meetup, context={'request': request})
        return Response(serializer.data)

    auth_error = ensure_authenticated(request)
    if auth_error:
        return auth_error

    meetup_user, profile_error = get_meetup_user_or_response(request)
    if profile_error:
        return profile_error

    permission_error = ensure_meetup_creator_or_admin(meetup, meetup_user)
    if permission_error:
        return permission_error

    if request.method == 'PUT':
        serializer = MeetupSerializer(meetup, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    meetup.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def user_meetups(request):
    auth_error = ensure_authenticated(request)
    if auth_error:
        return auth_error

    meetup_user, profile_error = get_meetup_user_or_response(request)
    if profile_error:
        return profile_error

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
            return Response(
                {'error': 'month 파라미터 형식은 YYYY-MM 이어야 합니다.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

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
    meetup, error = get_meetup_or_response(meetup_id)
    if error:
        return error

    registrations = Registration.objects.filter(meetup=meetup).select_related('user')
    registration_data = [{
        'id': reg.id,
        'user_name': reg.user.name,
        'user_email': reg.user.email,
        'registered_at': reg.registered_at
    } for reg in registrations]

    return Response({'meetup_id': meetup_id, 'registrations': registration_data}, status=status.HTTP_200_OK)


@api_view(['POST'])
def register_for_meetup(request, meetup_id):
    auth_error = ensure_authenticated(request)
    if auth_error:
        return auth_error

    meetup, meetup_error = get_meetup_or_response(meetup_id)
    if meetup_error:
        return meetup_error

    meetup_user, profile_error = get_meetup_user_or_response(request)
    if profile_error:
        return profile_error

    if Registration.objects.filter(user=meetup_user, meetup=meetup).exists():
        return Response({'error': '이미 이 모임에 신청되어 있습니다'}, status=status.HTTP_400_BAD_REQUEST)

    if Waitlist.objects.filter(user=meetup_user, meetup=meetup).exists():
        return Response({'error': '이미 이 모임 대기열에 등록되어 있습니다'}, status=status.HTTP_400_BAD_REQUEST)

    if meetup.is_full:
        return Response({
            'error': '모임 정원이 가득 찼습니다',
            'can_waitlist': True,
            'message': '대기열에 등록하시겠습니까?'
        }, status=status.HTTP_400_BAD_REQUEST)

    registration = Registration.objects.create(user=meetup_user, meetup=meetup)
    return Response({'message': '신청이 완료되었습니다', 'registration_id': registration.id}, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
def unregister_from_meetup(request, meetup_id):
    auth_error = ensure_authenticated(request)
    if auth_error:
        return auth_error

    meetup, meetup_error = get_meetup_or_response(meetup_id)
    if meetup_error:
        return meetup_error

    meetup_user, profile_error = get_meetup_user_or_response(request)
    if profile_error:
        return profile_error

    try:
        registration = Registration.objects.get(user=meetup_user, meetup=meetup)
    except Registration.DoesNotExist:
        return Response({'error': '신청 정보를 찾을 수 없습니다'}, status=status.HTTP_404_NOT_FOUND)

    registration.delete()
    return Response({'message': '신청 취소가 완료되었습니다'}, status=status.HTTP_200_OK)


@api_view(['GET'])
def check_registration_status(request, meetup_id):
    auth_error = ensure_authenticated(request, {'is_registered': False}, status.HTTP_200_OK)
    if auth_error:
        return auth_error

    meetup, meetup_error = get_meetup_or_response(meetup_id)
    if meetup_error:
        return meetup_error

    meetup_user, profile_error = get_meetup_user_or_response(request, {'is_registered': False}, status.HTTP_200_OK)
    if profile_error:
        return profile_error

    is_registered = Registration.objects.filter(user=meetup_user, meetup=meetup).exists()
    return Response({'is_registered': is_registered, 'meetup_id': meetup_id}, status=status.HTTP_200_OK)


@api_view(['POST'])
def add_participant_by_email(request, meetup_id):
    auth_error = ensure_authenticated(request)
    if auth_error:
        return auth_error

    meetup, meetup_error = get_meetup_or_response(meetup_id)
    if meetup_error:
        return meetup_error

    meetup_user, profile_error = get_meetup_user_or_response(request)
    if profile_error:
        return profile_error

    permission_error = ensure_meetup_creator(meetup, meetup_user, '모임 생성자만 참가자를 추가할 수 있습니다')
    if permission_error:
        return permission_error

    email = request.data.get('email')
    if not email:
        return Response({'error': '이메일이 필요합니다'}, status=status.HTTP_400_BAD_REQUEST)

    if meetup.is_full:
        return Response({'error': '모임 정원이 가득 찼습니다'}, status=status.HTTP_400_BAD_REQUEST)

    participant_user = _resolve_participant(email)

    if Registration.objects.filter(user=participant_user, meetup=meetup).exists():
        return Response({'error': '이미 이 모임에 등록된 사용자입니다'}, status=status.HTTP_400_BAD_REQUEST)

    registration = Registration.objects.create(user=participant_user, meetup=meetup)
    return Response({
        'message': '참가자가 성공적으로 추가되었습니다',
        'participant': {
            'id': participant_user.id,
            'name': participant_user.name,
            'email': participant_user.email,
            'registration_id': registration.id
        }
    }, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
def remove_participant(request, meetup_id, registration_id):
    auth_error = ensure_authenticated(request)
    if auth_error:
        return auth_error

    meetup, meetup_error = get_meetup_or_response(meetup_id)
    if meetup_error:
        return meetup_error

    meetup_user, profile_error = get_meetup_user_or_response(request)
    if profile_error:
        return profile_error

    permission_error = ensure_meetup_creator(meetup, meetup_user, '모임 생성자만 참가자를 제거할 수 있습니다')
    if permission_error:
        return permission_error

    try:
        registration = Registration.objects.get(id=registration_id, meetup=meetup)
    except Registration.DoesNotExist:
        return Response({'error': '신청 정보를 찾을 수 없습니다'}, status=status.HTTP_404_NOT_FOUND)

    registration.delete()
    return Response({'message': '참가자가 성공적으로 제거되었습니다'}, status=status.HTTP_200_OK)


def _resolve_participant(email):
    """
    Resolve an existing participant or create a new MeetupUser guest profile.
    """
    try:
        django_user = User.objects.get(email=email)
        return get_or_create_meetup_profile(django_user)
    except User.DoesNotExist:
        try:
            return MeetupUser.objects.get(email=email, user__isnull=True)
        except MeetupUser.DoesNotExist:
            return MeetupUser.objects.create(name=f"Guest ({email})", email=email, is_admin=False)
