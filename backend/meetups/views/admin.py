from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..models import Meetup, MeetupUser, Notification, Registration, Waitlist
from ..serializers import MeetupUserSerializer
from .helpers import APIResponse, get_object_or_error, require_admin


@api_view(['GET'])
@require_admin
def admin_users_list(request):
    """관리자: 사용자 목록 조회"""
    users = MeetupUser.objects.all().order_by('-created_at')
    serializer = MeetupUserSerializer(users, many=True)

    users_data = []
    for user_data in serializer.data:
        user = MeetupUser.objects.get(id=user_data['id'])
        user_data['created_meetups_count'] = user.created_meetups.count()
        user_data['registered_meetups_count'] = Registration.objects.filter(user=user).count()
        users_data.append(user_data)

    return Response(users_data)


@api_view(['GET'])
@require_admin
def admin_meetups_list(request):
    """관리자: 밋업 목록 조회"""
    meetups = Meetup.objects.all().order_by('-created_at')
    meetups_data = []

    for meetup in meetups:
        meetups_data.append({
            'id': meetup.id,
            'name': meetup.name,
            'description': meetup.description,
            'date_time': meetup.date_time,
            'end_time': meetup.end_time,
            'location': meetup.location,
            'max_participants': meetup.max_participants,
            'current_participants': meetup.current_participants,
            'is_full': meetup.is_full,
            'available_spots': meetup.available_spots,
            'creator_name': meetup.creator.name if meetup.creator else 'Unknown',
            'creator_id': meetup.creator.id if meetup.creator else None,
            'created_at': meetup.created_at,
            'registrations_count': Registration.objects.filter(meetup=meetup).count()
        })

    return Response(meetups_data)


@api_view(['DELETE'])
@require_admin
def admin_delete_user(request, user_id):
    """관리자: 사용자 삭제"""
    meetup_user, error = get_object_or_error(MeetupUser, '사용자를 찾을 수 없습니다', id=user_id)
    if error:
        return error

    if meetup_user.is_admin:
        return APIResponse.error('관리자는 삭제할 수 없습니다')

    try:
        with transaction.atomic():
            meetup_user.created_meetups.update(creator=None)
            Registration.objects.filter(user=meetup_user).delete()
            Waitlist.objects.filter(user=meetup_user).delete()
            Notification.objects.filter(user=meetup_user).delete()

            if meetup_user.user:
                meetup_user.user.delete()
            else:
                meetup_user.delete()
    except Exception as exc:
        return APIResponse.error(f'삭제 중 오류가 발생했습니다: {str(exc)}', status.HTTP_500_INTERNAL_SERVER_ERROR)

    return APIResponse.success(message='사용자가 성공적으로 삭제되었습니다')


@api_view(['DELETE'])
@require_admin
def admin_delete_meetup(request, meetup_id):
    """관리자: 밋업 삭제"""
    meetup, error = get_object_or_error(Meetup, '모임을 찾을 수 없습니다', id=meetup_id)
    if error:
        return error

    meetup.delete()
    return APIResponse.success(message='모임이 성공적으로 삭제되었습니다')


@api_view(['POST'])
@require_admin
def admin_toggle_user_admin(request, user_id):
    """관리자: 사용자 관리자 권한 토글"""
    meetup_user, error = get_object_or_error(MeetupUser, '사용자를 찾을 수 없습니다', id=user_id)
    if error:
        return error

    meetup_user.is_admin = not meetup_user.is_admin
    meetup_user.save()

    return APIResponse.success({
        'message': f'사용자 관리자 권한이 {"활성화" if meetup_user.is_admin else "비활성화"}되었습니다',
        'is_admin': meetup_user.is_admin
    })


@api_view(['GET'])
@require_admin
def admin_statistics(request):
    """관리자: 통계 조회"""
    total_users = MeetupUser.objects.count()
    total_meetups = Meetup.objects.count()
    total_registrations = Registration.objects.count()
    admin_users = MeetupUser.objects.filter(is_admin=True).count()

    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_users = MeetupUser.objects.filter(created_at__gte=thirty_days_ago).count()
    recent_meetups = Meetup.objects.filter(created_at__gte=thirty_days_ago).count()
    recent_registrations = Registration.objects.filter(registered_at__gte=thirty_days_ago).count()

    return APIResponse.success({
        'total_users': total_users,
        'total_meetups': total_meetups,
        'total_registrations': total_registrations,
        'admin_users': admin_users,
        'recent_users': recent_users,
        'recent_meetups': recent_meetups,
        'recent_registrations': recent_registrations
    })


@api_view(['POST'])
@require_admin
def admin_reset_user_password(request, user_id):
    """관리자: 사용자 비밀번호를 00000000으로 리셋"""
    meetup_user, error = get_object_or_error(MeetupUser, '사용자를 찾을 수 없습니다', id=user_id)
    if error:
        return error

    if not meetup_user.user:
        return APIResponse.error('Django 사용자 계정이 없습니다')

    # 비밀번호를 00000000으로 리셋
    meetup_user.user.set_password('00000000')
    meetup_user.user.save()

    return APIResponse.success(message=f'{meetup_user.name}님의 비밀번호를 00000000으로 리셋했습니다')
