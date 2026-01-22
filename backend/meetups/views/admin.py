from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..models import Meetup, MeetupUser, Notification, Registration, Waitlist
from ..serializers import MeetupUserSerializer
from .helpers import get_meetup_or_response


def is_admin_user(request):
    if not request.user.is_authenticated:
        return False
    try:
        return request.user.is_staff or request.user.meetup_profile.is_admin
    except MeetupUser.DoesNotExist:
        return request.user.is_staff


@api_view(['GET'])
def admin_users_list(request):
    if not is_admin_user(request):
        return Response({'error': '관리자 권한이 필요합니다'}, status=status.HTTP_403_FORBIDDEN)

    users = MeetupUser.objects.all().order_by('-created_at')
    serializer = MeetupUserSerializer(users, many=True)

    users_data = []
    for user_data in serializer.data:
        user = MeetupUser.objects.get(id=user_data['id'])
        user_data['created_meetups_count'] = user.created_meetups.count()
        user_data['registered_meetups_count'] = Registration.objects.filter(user=user).count()
        users_data.append(user_data)

    return Response(users_data, status=status.HTTP_200_OK)


@api_view(['GET'])
def admin_meetups_list(request):
    if not is_admin_user(request):
        return Response({'error': '관리자 권한이 필요합니다'}, status=status.HTTP_403_FORBIDDEN)

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

    return Response(meetups_data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
def admin_delete_user(request, user_id):
    if not is_admin_user(request):
        return Response({'error': '관리자 권한이 필요합니다'}, status=status.HTTP_403_FORBIDDEN)

    try:
        meetup_user = MeetupUser.objects.get(id=user_id)
    except MeetupUser.DoesNotExist:
        return Response({'error': '사용자를 찾을 수 없습니다'}, status=status.HTTP_404_NOT_FOUND)

    if meetup_user.is_admin:
        return Response({'error': '관리자는 삭제할 수 없습니다'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        with transaction.atomic():
            meetup_user.created_meetups.update(creator=None)
            for registration in Registration.objects.filter(user=meetup_user):
                registration.delete()
            for waitlist_entry in Waitlist.objects.filter(user=meetup_user):
                waitlist_entry.delete()
            Notification.objects.filter(user=meetup_user).delete()

            if meetup_user.user:
                meetup_user.user.delete()
            else:
                meetup_user.delete()
    except Exception as exc:  # pragma: no cover - defensive
        return Response({'error': f'삭제 중 오류가 발생했습니다: {str(exc)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({'message': '사용자가 성공적으로 삭제되었습니다'}, status=status.HTTP_200_OK)


@api_view(['DELETE'])
def admin_delete_meetup(request, meetup_id):
    if not is_admin_user(request):
        return Response({'error': '관리자 권한이 필요합니다'}, status=status.HTTP_403_FORBIDDEN)

    meetup, error = get_meetup_or_response(meetup_id)
    if error:
        return error

    meetup.delete()
    return Response({'message': '모임이 성공적으로 삭제되었습니다'}, status=status.HTTP_200_OK)


@api_view(['POST'])
def admin_toggle_user_admin(request, user_id):
    if not is_admin_user(request):
        return Response({'error': '관리자 권한이 필요합니다'}, status=status.HTTP_403_FORBIDDEN)

    try:
        meetup_user = MeetupUser.objects.get(id=user_id)
    except MeetupUser.DoesNotExist:
        return Response({'error': '사용자를 찾을 수 없습니다'}, status=status.HTTP_404_NOT_FOUND)

    meetup_user.is_admin = not meetup_user.is_admin
    meetup_user.save()

    return Response({
        'message': f'사용자 관리자 권한이 {"활성화" if meetup_user.is_admin else "비활성화"}되었습니다',
        'is_admin': meetup_user.is_admin
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
def admin_statistics(request):
    if not is_admin_user(request):
        return Response({'error': '관리자 권한이 필요합니다'}, status=status.HTTP_403_FORBIDDEN)

    total_users = MeetupUser.objects.count()
    total_meetups = Meetup.objects.count()
    total_registrations = Registration.objects.count()
    admin_users = MeetupUser.objects.filter(is_admin=True).count()

    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_users = MeetupUser.objects.filter(created_at__gte=thirty_days_ago).count()
    recent_meetups = Meetup.objects.filter(created_at__gte=thirty_days_ago).count()
    recent_registrations = Registration.objects.filter(registered_at__gte=thirty_days_ago).count()

    return Response({
        'total_users': total_users,
        'total_meetups': total_meetups,
        'total_registrations': total_registrations,
        'admin_users': admin_users,
        'recent_users': recent_users,
        'recent_meetups': recent_meetups,
        'recent_registrations': recent_registrations
    }, status=status.HTTP_200_OK)
