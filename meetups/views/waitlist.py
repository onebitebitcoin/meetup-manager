from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..models import Registration, Waitlist
from ..serializers import WaitlistSerializer
from .helpers import (
    ensure_authenticated,
    ensure_meetup_creator_or_admin,
    get_meetup_or_response,
    get_meetup_user_or_response,
)


@api_view(['POST'])
def add_to_waitlist(request, meetup_id):
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

    waitlist_entry = Waitlist.objects.create(user=meetup_user, meetup=meetup)
    return Response({
        'message': f'대기열 {waitlist_entry.position}번째로 등록되었습니다',
        'position': waitlist_entry.position,
        'waitlist_id': waitlist_entry.id
    }, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
def remove_from_waitlist(request, meetup_id):
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
        waitlist_entry = Waitlist.objects.get(user=meetup_user, meetup=meetup)
    except Waitlist.DoesNotExist:
        return Response({'error': '대기열에 등록되지 않았습니다'}, status=status.HTTP_404_NOT_FOUND)

    waitlist_entry.delete()
    return Response({'message': '대기열에서 제거되었습니다'}, status=status.HTTP_200_OK)


@api_view(['GET'])
def check_waitlist_status(request, meetup_id):
    auth_error = ensure_authenticated(request, {'is_waitlisted': False}, status.HTTP_200_OK)
    if auth_error:
        return auth_error

    meetup, meetup_error = get_meetup_or_response(meetup_id)
    if meetup_error:
        return meetup_error

    meetup_user, profile_error = get_meetup_user_or_response(request, {'is_waitlisted': False}, status.HTTP_200_OK)
    if profile_error:
        return profile_error

    try:
        waitlist_entry = Waitlist.objects.get(user=meetup_user, meetup=meetup)
        return Response({
            'is_waitlisted': True,
            'position': waitlist_entry.position,
            'waitlist_id': waitlist_entry.id,
            'meetup_id': meetup_id
        }, status=status.HTTP_200_OK)
    except Waitlist.DoesNotExist:
        return Response({'is_waitlisted': False, 'meetup_id': meetup_id}, status=status.HTTP_200_OK)


@api_view(['GET'])
def meetup_waitlist(request, meetup_id):
    auth_error = ensure_authenticated(request)
    if auth_error:
        return auth_error

    meetup, meetup_error = get_meetup_or_response(meetup_id)
    if meetup_error:
        return meetup_error

    meetup_user, profile_error = get_meetup_user_or_response(request)
    if profile_error:
        return profile_error

    permission_error = ensure_meetup_creator_or_admin(meetup, meetup_user)
    if permission_error:
        return permission_error

    waitlist_entries = Waitlist.objects.filter(meetup=meetup).select_related('user')
    waitlist_data = [{
        'id': entry.id,
        'position': entry.position,
        'user_name': entry.user.name,
        'user_email': entry.user.email,
        'waitlisted_at': entry.waitlisted_at
    } for entry in waitlist_entries]

    return Response({
        'meetup_id': meetup_id,
        'waitlist': waitlist_data,
        'total_waitlisted': len(waitlist_data)
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
def user_waitlists(request):
    auth_error = ensure_authenticated(request)
    if auth_error:
        return auth_error

    meetup_user, profile_error = get_meetup_user_or_response(request)
    if profile_error:
        return profile_error

    waitlists = Waitlist.objects.filter(user=meetup_user).select_related('meetup').order_by('meetup__date_time')
    serializer = WaitlistSerializer(waitlists, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
