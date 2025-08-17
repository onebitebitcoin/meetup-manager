from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.middleware.csrf import get_token
from .models import MeetupUser, Meetup, Registration, Waitlist, Notification
from .serializers import (
    MeetupUserSerializer, 
    MeetupSerializer, 
    RegistrationSerializer,
    RegisterUserSerializer,
    UserRegistrationSerializer,
    WaitlistSerializer,
    NotificationSerializer
)

@ensure_csrf_cookie
def get_csrf_token(request):
    token = get_token(request)
    print(f"CSRF token requested: {token[:10]}...")
    print(f"Request origin: {request.META.get('HTTP_ORIGIN')}")
    print(f"Request referer: {request.META.get('HTTP_REFERER')}")
    return JsonResponse({'csrfToken': token})

@api_view(['POST'])
@csrf_exempt
def register_new_user(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        try:
            user = serializer.save()
            return Response({
                'message': '사용자 등록이 완료되었습니다',
                'username': user.username
            }, status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response({
                'error': '사용자명 또는 이메일이 이미 존재합니다'
            }, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
    
    # Authenticate strictly by username (no email fallback)
    user = authenticate(username=username, password=password)
    if user:
        login(request, user)
        try:
            meetup_user = user.meetup_profile
            return Response({
                'message': '로그인 성공',
                'user': {
                    'id': meetup_user.id,
                    'username': user.username,
                    'name': meetup_user.name,
                    'email': meetup_user.email,
                    'is_admin': meetup_user.is_admin or user.is_staff
                }
            }, status=status.HTTP_200_OK)
        except MeetupUser.DoesNotExist:
            return Response({'error': '사용자 프로필을 찾을 수 없습니다'}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({'error': '잘못된 로그인 정보입니다'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
def logout_user(request):
    logout(request)
    return Response({'message': '로그아웃 성공'}, status=status.HTTP_200_OK)

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
        if self.request.user.is_authenticated:
            try:
                meetup_user = self.request.user.meetup_profile
                serializer.save(creator=meetup_user)
            except MeetupUser.DoesNotExist:
                serializer.save()
        else:
            serializer.save()

@api_view(['GET', 'PUT', 'DELETE'])
def meetup_detail(request, pk):
    try:
        meetup = Meetup.objects.get(pk=pk)
    except Meetup.DoesNotExist:
        return Response({'error': '모임을 찾을 수 없습니다'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = MeetupSerializer(meetup, context={'request': request})
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        if not request.user.is_authenticated:
            return Response({'error': '로그인이 필요합니다'}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            meetup_user = request.user.meetup_profile
            if meetup.creator != meetup_user and not meetup_user.is_admin:
                return Response({'error': '권한이 없습니다'}, status=status.HTTP_403_FORBIDDEN)
        except MeetupUser.DoesNotExist:
            return Response({'error': '사용자 프로필을 찾을 수 없습니다'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = MeetupSerializer(meetup, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        if not request.user.is_authenticated:
            return Response({'error': '로그인이 필요합니다'}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            meetup_user = request.user.meetup_profile
            if meetup.creator != meetup_user and not meetup_user.is_admin:
                return Response({'error': '권한이 없습니다'}, status=status.HTTP_403_FORBIDDEN)
        except MeetupUser.DoesNotExist:
            return Response({'error': '사용자 프로필을 찾을 수 없습니다'}, status=status.HTTP_404_NOT_FOUND)
        
        meetup.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def user_meetups(request):
    if not request.user.is_authenticated:
        return Response({'error': '로그인이 필요합니다'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        meetup_user = request.user.meetup_profile
        meetups = meetup_user.created_meetups.all().order_by('date_time')
        serializer = MeetupSerializer(meetups, many=True, context={'request': request})
        return Response(serializer.data)
    except MeetupUser.DoesNotExist:
        return Response({'error': '사용자 프로필을 찾을 수 없습니다'}, status=status.HTTP_404_NOT_FOUND)

class RegistrationListView(generics.ListAPIView):
    queryset = Registration.objects.all().order_by('-registered_at')
    serializer_class = RegistrationSerializer

@api_view(['POST'])
def register_user(request):
    serializer = RegisterUserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        meetup = serializer.validated_data['meetup']
        
        registration = Registration.objects.create(user=user, meetup=meetup)
        
        response_serializer = RegistrationSerializer(registration)
        return Response({
            'message': '신청이 완료되었습니다',
            'registration': response_serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def health_check(request):
    return JsonResponse({'status': 'ok', 'message': 'Django 백엔드가 실행 중입니다'})

@api_view(['GET'])
def meetup_registrations(request, meetup_id):
    try:
        meetup = Meetup.objects.get(id=meetup_id)
        registrations = Registration.objects.filter(meetup=meetup).select_related('user')
        
        registration_data = []
        for reg in registrations:
            # Mask email for privacy: show first 3 chars + *** + domain
            email = reg.user.email
            username, domain = email.split('@')
            masked_email = username[:3] + '***@' + domain if len(username) > 3 else username[0] + '***@' + domain
            
            registration_data.append({
                'id': reg.id,
                'user_name': reg.user.name,
                'user_email': masked_email,
                'registered_at': reg.registered_at
            })
        
        return Response({
            'meetup_id': meetup_id,
            'registrations': registration_data
        }, status=status.HTTP_200_OK)
        
    except Meetup.DoesNotExist:
        return Response({'error': '모임을 찾을 수 없습니다'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def register_for_meetup(request, meetup_id):
    if not request.user.is_authenticated:
        return Response({'error': '로그인이 필요합니다'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        meetup = Meetup.objects.get(id=meetup_id)
        meetup_user = request.user.meetup_profile
        
        # Check if already registered
        if Registration.objects.filter(user=meetup_user, meetup=meetup).exists():
            return Response({'error': '이미 이 모임에 신청되어 있습니다'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if already in waitlist
        if Waitlist.objects.filter(user=meetup_user, meetup=meetup).exists():
            return Response({'error': '이미 이 모임 대기열에 등록되어 있습니다'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if meetup is full - if so, suggest joining waitlist
        if meetup.is_full:
            return Response({
                'error': '모임 정원이 가득 찼습니다',
                'can_waitlist': True,
                'message': '대기열에 등록하시겠습니까?'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create registration
        registration = Registration.objects.create(user=meetup_user, meetup=meetup)
        
        return Response({
            'message': '신청이 완료되었습니다',
            'registration_id': registration.id
        }, status=status.HTTP_201_CREATED)
        
    except Meetup.DoesNotExist:
        return Response({'error': '모임을 찾을 수 없습니다'}, status=status.HTTP_404_NOT_FOUND)
    except MeetupUser.DoesNotExist:
        return Response({'error': '사용자 프로필을 찾을 수 없습니다'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
def unregister_from_meetup(request, meetup_id):
    if not request.user.is_authenticated:
        return Response({'error': '로그인이 필요합니다'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        meetup = Meetup.objects.get(id=meetup_id)
        meetup_user = request.user.meetup_profile
        
        registration = Registration.objects.get(user=meetup_user, meetup=meetup)
        registration.delete()
        
        return Response({
            'message': '신청 취소가 완료되었습니다'
        }, status=status.HTTP_200_OK)
        
    except Meetup.DoesNotExist:
        return Response({'error': '모임을 찾을 수 없습니다'}, status=status.HTTP_404_NOT_FOUND)
    except Registration.DoesNotExist:
        return Response({'error': '신청 정보를 찾을 수 없습니다'}, status=status.HTTP_404_NOT_FOUND)
    except MeetupUser.DoesNotExist:
        return Response({'error': '사용자 프로필을 찾을 수 없습니다'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def check_registration_status(request, meetup_id):
    if not request.user.is_authenticated:
        return Response({'is_registered': False}, status=status.HTTP_200_OK)
    
    try:
        meetup = Meetup.objects.get(id=meetup_id)
        meetup_user = request.user.meetup_profile
        
        is_registered = Registration.objects.filter(user=meetup_user, meetup=meetup).exists()
        
        return Response({
            'is_registered': is_registered,
            'meetup_id': meetup_id
        }, status=status.HTTP_200_OK)
        
    except Meetup.DoesNotExist:
        return Response({'error': '모임을 찾을 수 없습니다'}, status=status.HTTP_404_NOT_FOUND)
    except MeetupUser.DoesNotExist:
        return Response({'is_registered': False}, status=status.HTTP_200_OK)

# Admin-specific views
def is_admin_user(request):
    """Helper function to check if user is admin"""
    if not request.user.is_authenticated:
        return False
    try:
        # Check Django user is_staff OR meetup_profile is_admin
        return request.user.is_staff or request.user.meetup_profile.is_admin
    except MeetupUser.DoesNotExist:
        return request.user.is_staff

@api_view(['GET'])
def admin_users_list(request):
    """Get all users for admin view"""
    if not is_admin_user(request):
        return Response({'error': '관리자 권한이 필요합니다'}, status=status.HTTP_403_FORBIDDEN)
    
    users = MeetupUser.objects.all().order_by('-created_at')
    serializer = MeetupUserSerializer(users, many=True)
    
    # Add additional info for admin view
    users_data = []
    for user_data in serializer.data:
        user = MeetupUser.objects.get(id=user_data['id'])
        created_meetups = user.created_meetups.count()
        registrations = Registration.objects.filter(user=user).count()
        
        user_data['created_meetups_count'] = created_meetups
        user_data['registered_meetups_count'] = registrations
        users_data.append(user_data)
    
    return Response(users_data, status=status.HTTP_200_OK)

@api_view(['GET'])
def admin_meetups_list(request):
    """Get all meetups for admin view"""
    if not is_admin_user(request):
        return Response({'error': '관리자 권한이 필요합니다'}, status=status.HTTP_403_FORBIDDEN)
    
    meetups = Meetup.objects.all().order_by('-created_at')
    meetups_data = []
    
    for meetup in meetups:
        meetup_data = {
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
        }
        meetups_data.append(meetup_data)
    
    return Response(meetups_data, status=status.HTTP_200_OK)

@api_view(['DELETE'])
def admin_delete_user(request, user_id):
    """Delete a user (admin only)"""
    if not is_admin_user(request):
        return Response({'error': '관리자 권한이 필요합니다'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        meetup_user = MeetupUser.objects.get(id=user_id)
        
        # Prevent deleting admin users
        if meetup_user.is_admin:
            return Response({'error': '관리자는 삭제할 수 없습니다'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Delete associated Django user if exists
        if meetup_user.user:
            meetup_user.user.delete()
        else:
            meetup_user.delete()
            
        return Response({'message': '사용자가 성공적으로 삭제되었습니다'}, status=status.HTTP_200_OK)
        
    except MeetupUser.DoesNotExist:
        return Response({'error': '사용자를 찾을 수 없습니다'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
def admin_delete_meetup(request, meetup_id):
    """Delete a meetup (admin only)"""
    if not is_admin_user(request):
        return Response({'error': '관리자 권한이 필요합니다'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        meetup = Meetup.objects.get(id=meetup_id)
        meetup.delete()
        return Response({'message': '모임이 성공적으로 삭제되었습니다'}, status=status.HTTP_200_OK)
        
    except Meetup.DoesNotExist:
        return Response({'error': '모임을 찾을 수 없습니다'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def admin_toggle_user_admin(request, user_id):
    """Toggle admin status for a user (admin only)"""
    if not is_admin_user(request):
        return Response({'error': '관리자 권한이 필요합니다'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        meetup_user = MeetupUser.objects.get(id=user_id)
        meetup_user.is_admin = not meetup_user.is_admin
        meetup_user.save()
        
        return Response({
            'message': f'사용자 관리자 권한이 {"활성화" if meetup_user.is_admin else "비활성화"}되었습니다',
            'is_admin': meetup_user.is_admin
        }, status=status.HTTP_200_OK)
        
    except MeetupUser.DoesNotExist:
        return Response({'error': '사용자를 찾을 수 없습니다'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def admin_statistics(request):
    """Get dashboard statistics for admin"""
    if not is_admin_user(request):
        return Response({'error': '관리자 권한이 필요합니다'}, status=status.HTTP_403_FORBIDDEN)
    
    total_users = MeetupUser.objects.count()
    total_meetups = Meetup.objects.count()
    total_registrations = Registration.objects.count()
    admin_users = MeetupUser.objects.filter(is_admin=True).count()
    
    # Recent activity (last 30 days)
    from django.utils import timezone
    from datetime import timedelta
    
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

@api_view(['POST'])
def add_participant_by_email(request, meetup_id):
    """Add a participant to meetup by email (for meetup creators)"""
    if not request.user.is_authenticated:
        return Response({'error': '로그인이 필요합니다'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        meetup = Meetup.objects.get(id=meetup_id)
        meetup_user = request.user.meetup_profile
        
        # Check if user is the creator of the meetup
        if meetup.creator != meetup_user:
            return Response({'error': '모임 생성자만 참가자를 추가할 수 있습니다'}, status=status.HTTP_403_FORBIDDEN)
        
        email = request.data.get('email')
        if not email:
            return Response({'error': '이메일이 필요합니다'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if meetup is full
        if meetup.is_full:
            return Response({'error': '모임 정원이 가득 찼습니다'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Try to find existing user with this email
        participant_user = None
        try:
            # First try to find by MeetupUser email
            participant_user = MeetupUser.objects.get(email=email)
        except MeetupUser.DoesNotExist:
            try:
                # Then try to find by Django User email
                django_user = User.objects.get(email=email)
                participant_user = django_user.meetup_profile
            except (User.DoesNotExist, MeetupUser.DoesNotExist):
                # Create a new MeetupUser without Django User (guest user)
                participant_user = MeetupUser.objects.create(
                    name=f"Guest ({email})",
                    email=email,
                    is_admin=False
                )
        
        # Check if already registered
        if Registration.objects.filter(user=participant_user, meetup=meetup).exists():
            return Response({'error': '이미 이 모임에 등록된 사용자입니다'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create registration
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
        
    except Meetup.DoesNotExist:
        return Response({'error': '모임을 찾을 수 없습니다'}, status=status.HTTP_404_NOT_FOUND)
    except MeetupUser.DoesNotExist:
        return Response({'error': '사용자 프로필을 찾을 수 없습니다'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
def remove_participant(request, meetup_id, registration_id):
    """Remove a participant from meetup (for meetup creators)"""
    if not request.user.is_authenticated:
        return Response({'error': '로그인이 필요합니다'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        meetup = Meetup.objects.get(id=meetup_id)
        meetup_user = request.user.meetup_profile
        
        # Check if user is the creator of the meetup
        if meetup.creator != meetup_user:
            return Response({'error': '모임 생성자만 참가자를 제거할 수 있습니다'}, status=status.HTTP_403_FORBIDDEN)
        
        registration = Registration.objects.get(id=registration_id, meetup=meetup)
        registration.delete()
        
        return Response({'message': '참가자가 성공적으로 제거되었습니다'}, status=status.HTTP_200_OK)
        
    except Meetup.DoesNotExist:
        return Response({'error': '모임을 찾을 수 없습니다'}, status=status.HTTP_404_NOT_FOUND)
    except Registration.DoesNotExist:
        return Response({'error': '신청 정보를 찾을 수 없습니다'}, status=status.HTTP_404_NOT_FOUND)
    except MeetupUser.DoesNotExist:
        return Response({'error': '사용자 프로필을 찾을 수 없습니다'}, status=status.HTTP_404_NOT_FOUND)


# Waitlist API endpoints
@api_view(['POST'])
def add_to_waitlist(request, meetup_id):
    """Add user to meetup waitlist"""
    if not request.user.is_authenticated:
        return Response({'error': '로그인이 필요합니다'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        meetup = Meetup.objects.get(id=meetup_id)
        meetup_user = request.user.meetup_profile
        
        # Check if already registered
        if Registration.objects.filter(user=meetup_user, meetup=meetup).exists():
            return Response({'error': '이미 이 모임에 신청되어 있습니다'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if already in waitlist
        if Waitlist.objects.filter(user=meetup_user, meetup=meetup).exists():
            return Response({'error': '이미 이 모임 대기열에 등록되어 있습니다'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Add to waitlist
        waitlist_entry = Waitlist.objects.create(user=meetup_user, meetup=meetup)
        
        return Response({
            'message': f'대기열 {waitlist_entry.position}번째로 등록되었습니다',
            'position': waitlist_entry.position,
            'waitlist_id': waitlist_entry.id
        }, status=status.HTTP_201_CREATED)
        
    except Meetup.DoesNotExist:
        return Response({'error': '모임을 찾을 수 없습니다'}, status=status.HTTP_404_NOT_FOUND)
    except MeetupUser.DoesNotExist:
        return Response({'error': '사용자 프로필을 찾을 수 없습니다'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
def remove_from_waitlist(request, meetup_id):
    """Remove user from meetup waitlist"""
    if not request.user.is_authenticated:
        return Response({'error': '로그인이 필요합니다'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        meetup = Meetup.objects.get(id=meetup_id)
        meetup_user = request.user.meetup_profile
        
        waitlist_entry = Waitlist.objects.get(user=meetup_user, meetup=meetup)
        waitlist_entry.delete()
        
        return Response({
            'message': '대기열에서 제거되었습니다'
        }, status=status.HTTP_200_OK)
        
    except Meetup.DoesNotExist:
        return Response({'error': '모임을 찾을 수 없습니다'}, status=status.HTTP_404_NOT_FOUND)
    except Waitlist.DoesNotExist:
        return Response({'error': '대기열에 등록되지 않았습니다'}, status=status.HTTP_404_NOT_FOUND)
    except MeetupUser.DoesNotExist:
        return Response({'error': '사용자 프로필을 찾을 수 없습니다'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def check_waitlist_status(request, meetup_id):
    """Check if user is in waitlist and their position"""
    if not request.user.is_authenticated:
        return Response({'is_waitlisted': False}, status=status.HTTP_200_OK)
    
    try:
        meetup = Meetup.objects.get(id=meetup_id)
        meetup_user = request.user.meetup_profile
        
        try:
            waitlist_entry = Waitlist.objects.get(user=meetup_user, meetup=meetup)
            return Response({
                'is_waitlisted': True,
                'position': waitlist_entry.position,
                'waitlist_id': waitlist_entry.id,
                'meetup_id': meetup_id
            }, status=status.HTTP_200_OK)
        except Waitlist.DoesNotExist:
            return Response({
                'is_waitlisted': False,
                'meetup_id': meetup_id
            }, status=status.HTTP_200_OK)
        
    except Meetup.DoesNotExist:
        return Response({'error': '모임을 찾을 수 없습니다'}, status=status.HTTP_404_NOT_FOUND)
    except MeetupUser.DoesNotExist:
        return Response({'is_waitlisted': False}, status=status.HTTP_200_OK)


@api_view(['GET'])
def meetup_waitlist(request, meetup_id):
    """Get waitlist for a meetup (for creators and admins)"""
    if not request.user.is_authenticated:
        return Response({'error': '로그인이 필요합니다'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        meetup = Meetup.objects.get(id=meetup_id)
        meetup_user = request.user.meetup_profile
        
        # Check if user is creator or admin
        if meetup.creator != meetup_user and not meetup_user.is_admin:
            return Response({'error': '권한이 없습니다'}, status=status.HTTP_403_FORBIDDEN)
        
        waitlist_entries = Waitlist.objects.filter(meetup=meetup).select_related('user')
        
        waitlist_data = []
        for entry in waitlist_entries:
            # Mask email for privacy
            email = entry.user.email
            username, domain = email.split('@')
            masked_email = username[:3] + '***@' + domain if len(username) > 3 else username[0] + '***@' + domain
            
            waitlist_data.append({
                'id': entry.id,
                'position': entry.position,
                'user_name': entry.user.name,
                'user_email': masked_email,
                'waitlisted_at': entry.waitlisted_at
            })
        
        return Response({
            'meetup_id': meetup_id,
            'waitlist': waitlist_data,
            'total_waitlisted': len(waitlist_data)
        }, status=status.HTTP_200_OK)
        
    except Meetup.DoesNotExist:
        return Response({'error': '모임을 찾을 수 없습니다'}, status=status.HTTP_404_NOT_FOUND)
    except MeetupUser.DoesNotExist:
        return Response({'error': '사용자 프로필을 찾을 수 없습니다'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def user_waitlists(request):
    """Get all waitlists for the current user"""
    if not request.user.is_authenticated:
        return Response({'error': '로그인이 필요합니다'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        meetup_user = request.user.meetup_profile
        waitlists = Waitlist.objects.filter(user=meetup_user).select_related('meetup').order_by('meetup__date_time')
        serializer = WaitlistSerializer(waitlists, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except MeetupUser.DoesNotExist:
        return Response({'error': '사용자 프로필을 찾을 수 없습니다'}, status=status.HTTP_404_NOT_FOUND)


# Notification API endpoints
@api_view(['GET'])
def user_notifications(request):
    """Get all notifications for the current user"""
    if not request.user.is_authenticated:
        return Response({'error': '로그인이 필요합니다'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        meetup_user = request.user.meetup_profile
        notifications = Notification.objects.filter(user=meetup_user).select_related('meetup')
        serializer = NotificationSerializer(notifications, many=True)
        
        # Also return unread count
        unread_count = notifications.filter(is_read=False).count()
        
        return Response({
            'notifications': serializer.data,
            'unread_count': unread_count
        }, status=status.HTTP_200_OK)
    except MeetupUser.DoesNotExist:
        return Response({'error': '사용자 프로필을 찾을 수 없습니다'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def mark_notification_read(request, notification_id):
    """Mark a notification as read"""
    if not request.user.is_authenticated:
        return Response({'error': '로그인이 필요합니다'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        meetup_user = request.user.meetup_profile
        notification = Notification.objects.get(id=notification_id, user=meetup_user)
        notification.is_read = True
        notification.save()
        
        return Response({'message': '알림이 읽음 처리되었습니다'}, status=status.HTTP_200_OK)
    except Notification.DoesNotExist:
        return Response({'error': '알림을 찾을 수 없습니다'}, status=status.HTTP_404_NOT_FOUND)
    except MeetupUser.DoesNotExist:
        return Response({'error': '사용자 프로필을 찾을 수 없습니다'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def mark_all_notifications_read(request):
    """Mark all notifications as read for the current user"""
    if not request.user.is_authenticated:
        return Response({'error': '로그인이 필요합니다'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        meetup_user = request.user.meetup_profile
        updated_count = Notification.objects.filter(user=meetup_user, is_read=False).update(is_read=True)
        
        return Response({
            'message': f'{updated_count}개의 알림이 읽음 처리되었습니다',
            'updated_count': updated_count
        }, status=status.HTTP_200_OK)
    except MeetupUser.DoesNotExist:
        return Response({'error': '사용자 프로필을 찾을 수 없습니다'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
def delete_notification(request, notification_id):
    """Delete a notification"""
    if not request.user.is_authenticated:
        return Response({'error': '로그인이 필요합니다'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        meetup_user = request.user.meetup_profile
        notification = Notification.objects.get(id=notification_id, user=meetup_user)
        notification.delete()
        
        return Response({'message': '알림이 삭제되었습니다'}, status=status.HTTP_200_OK)
    except Notification.DoesNotExist:
        return Response({'error': '알림을 찾을 수 없습니다'}, status=status.HTTP_404_NOT_FOUND)
    except MeetupUser.DoesNotExist:
        return Response({'error': '사용자 프로필을 찾을 수 없습니다'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def send_notification_to_participants(request, meetup_id):
    """Send notification to all participants of a meetup"""
    if not request.user.is_authenticated:
        return Response({'error': '로그인이 필요합니다'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        meetup_user = request.user.meetup_profile
        meetup = Meetup.objects.get(id=meetup_id, creator=meetup_user)
        
        title = request.data.get('title')
        message = request.data.get('message')
        
        if not title or not message:
            return Response({'error': '제목과 메시지를 입력해주세요'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get all participants of this meetup
        registrations = Registration.objects.filter(meetup=meetup)
        
        if not registrations.exists():
            return Response({'error': '참가자가 없습니다'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create notifications for all participants
        notifications_created = []
        for registration in registrations:
            notification = Notification.objects.create(
                user=registration.user,
                title=title,
                message=message,
                notification_type='general',
                meetup=meetup
            )
            notifications_created.append(notification)
        
        return Response({
            'message': '알림이 성공적으로 전송되었습니다',
            'sent_count': len(notifications_created)
        }, status=status.HTTP_200_OK)
        
    except Meetup.DoesNotExist:
        return Response({'error': '모임을 찾을 수 없거나 권한이 없습니다'}, status=status.HTTP_404_NOT_FOUND)
    except MeetupUser.DoesNotExist:
        return Response({'error': '사용자 프로필을 찾을 수 없습니다'}, status=status.HTTP_404_NOT_FOUND)
