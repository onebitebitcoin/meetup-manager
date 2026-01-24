from rest_framework.decorators import api_view

from ..models import Meetup, Notification, Registration
from ..serializers import NotificationSerializer
from .helpers import APIResponse, get_object_or_error, require_profile


@api_view(['GET'])
@require_profile
def user_notifications(request):
    """사용자 알림 조회"""
    meetup_user = request.meetup_user

    notifications = Notification.objects.filter(user=meetup_user).select_related('meetup')
    serializer = NotificationSerializer(notifications, many=True)
    unread_count = notifications.filter(is_read=False).count()

    return APIResponse.success({
        'notifications': serializer.data,
        'unread_count': unread_count
    })


@api_view(['POST'])
@require_profile
def mark_notification_read(request, notification_id):
    """알림 읽음 처리"""
    meetup_user = request.meetup_user

    notification, error = get_object_or_error(
        Notification, '알림을 찾을 수 없습니다',
        id=notification_id, user=meetup_user
    )
    if error:
        return error

    notification.is_read = True
    notification.save()
    return APIResponse.success(message='알림이 읽음 처리되었습니다')


@api_view(['POST'])
@require_profile
def mark_all_notifications_read(request):
    """모든 알림 읽음 처리"""
    meetup_user = request.meetup_user

    updated_count = Notification.objects.filter(user=meetup_user, is_read=False).update(is_read=True)
    return APIResponse.success({
        'message': f'{updated_count}개의 알림이 읽음 처리되었습니다',
        'updated_count': updated_count
    })


@api_view(['DELETE'])
@require_profile
def delete_notification(request, notification_id):
    """알림 삭제"""
    meetup_user = request.meetup_user

    notification, error = get_object_or_error(
        Notification, '알림을 찾을 수 없습니다',
        id=notification_id, user=meetup_user
    )
    if error:
        return error

    notification.delete()
    return APIResponse.success(message='알림이 삭제되었습니다')


@api_view(['POST'])
@require_profile
def send_notification_to_participants(request, meetup_id):
    """참가자들에게 알림 전송 (생성자만)"""
    meetup_user = request.meetup_user

    # 생성자 권한 확인
    meetup, error = get_object_or_error(
        Meetup, '모임을 찾을 수 없거나 권한이 없습니다',
        id=meetup_id, creator=meetup_user
    )
    if error:
        return error

    title = request.data.get('title')
    message = request.data.get('message')
    if not title or not message:
        return APIResponse.error('제목과 메시지를 입력해주세요')

    registrations = Registration.objects.filter(meetup=meetup)
    if not registrations.exists():
        return APIResponse.error('참가자가 없습니다')

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

    return APIResponse.success({
        'message': '알림이 성공적으로 전송되었습니다',
        'sent_count': sent_count
    })
