from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..models import Registration, Waitlist
from ..serializers import WaitlistSerializer
from .helpers import (
    APIResponse,
    get_object_or_error,
    require_meetup_access,
    require_meetup_creator_or_admin,
    require_profile,
)


@api_view(['POST'])
@require_meetup_access('meetup_id')
def add_to_waitlist(request, meetup_id):
    """대기열 등록"""
    meetup = request.meetup
    meetup_user = request.meetup_user

    if Registration.objects.filter(user=meetup_user, meetup=meetup).exists():
        return APIResponse.error('이미 이 모임에 신청되어 있습니다')

    if Waitlist.objects.filter(user=meetup_user, meetup=meetup).exists():
        return APIResponse.error('이미 이 모임 대기열에 등록되어 있습니다')

    waitlist_entry = Waitlist.objects.create(user=meetup_user, meetup=meetup)
    return APIResponse.created({
        'message': f'대기열 {waitlist_entry.position}번째로 등록되었습니다',
        'position': waitlist_entry.position,
        'waitlist_id': waitlist_entry.id
    })


@api_view(['DELETE'])
@require_meetup_access('meetup_id')
def remove_from_waitlist(request, meetup_id):
    """대기열에서 제거"""
    meetup = request.meetup
    meetup_user = request.meetup_user

    waitlist_entry, error = get_object_or_error(
        Waitlist, '대기열에 등록되지 않았습니다',
        user=meetup_user, meetup=meetup
    )
    if error:
        return error

    waitlist_entry.delete()
    return APIResponse.success(message='대기열에서 제거되었습니다')


@api_view(['GET'])
def check_waitlist_status(request, meetup_id):
    """대기열 상태 확인"""
    # 비로그인 사용자는 is_waitlisted=False 반환
    if not request.user.is_authenticated:
        return APIResponse.success({'is_waitlisted': False})

    from ..models import Meetup
    meetup, error = get_object_or_error(Meetup, '모임을 찾을 수 없습니다', id=meetup_id)
    if error:
        return error

    from ..models import MeetupUser
    try:
        meetup_user = request.user.meetup_profile
    except MeetupUser.DoesNotExist:
        return APIResponse.success({'is_waitlisted': False})

    try:
        waitlist_entry = Waitlist.objects.get(user=meetup_user, meetup=meetup)
        return APIResponse.success({
            'is_waitlisted': True,
            'position': waitlist_entry.position,
            'waitlist_id': waitlist_entry.id,
            'meetup_id': meetup_id
        })
    except Waitlist.DoesNotExist:
        return APIResponse.success({'is_waitlisted': False, 'meetup_id': meetup_id})


@api_view(['GET'])
@require_meetup_creator_or_admin('meetup_id')
def meetup_waitlist(request, meetup_id):
    """밋업 대기열 목록 조회 (생성자/관리자만)"""
    meetup = request.meetup

    waitlist_entries = Waitlist.objects.filter(meetup=meetup).select_related('user')
    waitlist_data = [{
        'id': entry.id,
        'position': entry.position,
        'user_name': entry.user.name,
        'user_email': entry.user.email,
        'waitlisted_at': entry.waitlisted_at
    } for entry in waitlist_entries]

    return APIResponse.success({
        'meetup_id': meetup_id,
        'waitlist': waitlist_data,
        'total_waitlisted': len(waitlist_data)
    })


@api_view(['GET'])
@require_profile
def user_waitlists(request):
    """사용자의 대기열 목록 조회"""
    meetup_user = request.meetup_user

    waitlists = Waitlist.objects.filter(user=meetup_user).select_related('meetup').order_by('meetup__date_time')
    serializer = WaitlistSerializer(waitlists, many=True)
    return Response(serializer.data)
