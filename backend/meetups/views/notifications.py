from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..models import Meetup, Notification, Registration
from ..serializers import NotificationSerializer
from .helpers import ensure_authenticated, get_meetup_user_or_response


@api_view(['GET'])
def user_notifications(request):
    auth_error = ensure_authenticated(request)
    if auth_error:
        return auth_error

    meetup_user, profile_error = get_meetup_user_or_response(request)
    if profile_error:
        return profile_error

    notifications = Notification.objects.filter(user=meetup_user).select_related('meetup')
    serializer = NotificationSerializer(notifications, many=True)
    unread_count = notifications.filter(is_read=False).count()

    return Response({'notifications': serializer.data, 'unread_count': unread_count}, status=status.HTTP_200_OK)


@api_view(['POST'])
def mark_notification_read(request, notification_id):
    auth_error = ensure_authenticated(request)
    if auth_error:
        return auth_error

    meetup_user, profile_error = get_meetup_user_or_response(request)
    if profile_error:
        return profile_error

    try:
        notification = Notification.objects.get(id=notification_id, user=meetup_user)
    except Notification.DoesNotExist:
        return Response({'error': '알림을 찾을 수 없습니다'}, status=status.HTTP_404_NOT_FOUND)

    notification.is_read = True
    notification.save()
    return Response({'message': '알림이 읽음 처리되었습니다'}, status=status.HTTP_200_OK)


@api_view(['POST'])
def mark_all_notifications_read(request):
    auth_error = ensure_authenticated(request)
    if auth_error:
        return auth_error

    meetup_user, profile_error = get_meetup_user_or_response(request)
    if profile_error:
        return profile_error

    updated_count = Notification.objects.filter(user=meetup_user, is_read=False).update(is_read=True)
    return Response({
        'message': f'{updated_count}개의 알림이 읽음 처리되었습니다',
        'updated_count': updated_count
    }, status=status.HTTP_200_OK)


@api_view(['DELETE'])
def delete_notification(request, notification_id):
    auth_error = ensure_authenticated(request)
    if auth_error:
        return auth_error

    meetup_user, profile_error = get_meetup_user_or_response(request)
    if profile_error:
        return profile_error

    try:
        notification = Notification.objects.get(id=notification_id, user=meetup_user)
    except Notification.DoesNotExist:
        return Response({'error': '알림을 찾을 수 없습니다'}, status=status.HTTP_404_NOT_FOUND)

    notification.delete()
    return Response({'message': '알림이 삭제되었습니다'}, status=status.HTTP_200_OK)


@api_view(['POST'])
def send_notification_to_participants(request, meetup_id):
    auth_error = ensure_authenticated(request)
    if auth_error:
        return auth_error

    meetup_user, profile_error = get_meetup_user_or_response(request)
    if profile_error:
        return profile_error

    try:
        meetup = Meetup.objects.get(id=meetup_id, creator=meetup_user)
    except Meetup.DoesNotExist:
        return Response({'error': '모임을 찾을 수 없거나 권한이 없습니다'}, status=status.HTTP_404_NOT_FOUND)

    title = request.data.get('title')
    message = request.data.get('message')
    if not title or not message:
        return Response({'error': '제목과 메시지를 입력해주세요'}, status=status.HTTP_400_BAD_REQUEST)

    registrations = Registration.objects.filter(meetup=meetup)
    if not registrations.exists():
        return Response({'error': '참가자가 없습니다'}, status=status.HTTP_400_BAD_REQUEST)

    sent_count = 0
    for registration in registrations:
        Notification.objects.create(
            user=registration.user,
            title=title,
            message=message,
            notification_type='general',
            meetup=meetup
        )
        sent_count += 1

    return Response({'message': '알림이 성공적으로 전송되었습니다', 'sent_count': sent_count}, status=status.HTTP_200_OK)
