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
from .models import MeetupUser, Meetup, Registration
from .serializers import (
    MeetupUserSerializer, 
    MeetupSerializer, 
    RegistrationSerializer,
    RegisterUserSerializer,
    UserRegistrationSerializer
)

@ensure_csrf_cookie
def get_csrf_token(request):
    token = get_token(request)
    print(f"CSRF token requested: {token[:10]}...")
    print(f"Request origin: {request.META.get('HTTP_ORIGIN')}")
    print(f"Request referer: {request.META.get('HTTP_REFERER')}")
    return JsonResponse({'csrfToken': token})

@api_view(['POST'])
def register_new_user(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        try:
            user = serializer.save()
            return Response({
                'message': 'User registered successfully',
                'username': user.username
            }, status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response({
                'error': 'Username or email already exists'
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
        return Response({'error': 'Username and password required'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Try to authenticate with email if it looks like an email
    if '@' in username:
        try:
            user_obj = User.objects.get(email=username)
            user = authenticate(username=user_obj.username, password=password)
        except User.DoesNotExist:
            user = None
    else:
        user = authenticate(username=username, password=password)
    if user:
        login(request, user)
        try:
            meetup_user = user.meetup_profile
            return Response({
                'message': 'Login successful',
                'user': {
                    'id': meetup_user.id,
                    'username': user.username,
                    'name': meetup_user.name,
                    'email': meetup_user.email,
                    'is_admin': meetup_user.is_admin
                }
            }, status=status.HTTP_200_OK)
        except MeetupUser.DoesNotExist:
            return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
def logout_user(request):
    logout(request)
    return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)

class MeetupUserListCreateView(generics.ListCreateAPIView):
    queryset = MeetupUser.objects.all().order_by('-created_at')
    serializer_class = MeetupUserSerializer

@method_decorator(csrf_exempt, name='dispatch')
class MeetupListCreateView(generics.ListCreateAPIView):
    queryset = Meetup.objects.all().order_by('date_time')
    serializer_class = MeetupSerializer
    
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
        return Response({'error': 'Meetup not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = MeetupSerializer(meetup)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            meetup_user = request.user.meetup_profile
            if meetup.creator != meetup_user and not meetup_user.is_admin:
                return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        except MeetupUser.DoesNotExist:
            return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = MeetupSerializer(meetup, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            meetup_user = request.user.meetup_profile
            if meetup.creator != meetup_user and not meetup_user.is_admin:
                return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        except MeetupUser.DoesNotExist:
            return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)
        
        meetup.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def user_meetups(request):
    if not request.user.is_authenticated:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        meetup_user = request.user.meetup_profile
        meetups = meetup_user.created_meetups.all().order_by('date_time')
        serializer = MeetupSerializer(meetups, many=True)
        return Response(serializer.data)
    except MeetupUser.DoesNotExist:
        return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)

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
            'message': 'Registration successful',
            'registration': response_serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def health_check(request):
    return JsonResponse({'status': 'ok', 'message': 'Django backend is running'})

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
        return Response({'error': 'Meetup not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def register_for_meetup(request, meetup_id):
    if not request.user.is_authenticated:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        meetup = Meetup.objects.get(id=meetup_id)
        meetup_user = request.user.meetup_profile
        
        # Check if already registered
        if Registration.objects.filter(user=meetup_user, meetup=meetup).exists():
            return Response({'error': 'Already registered for this meetup'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if meetup is full
        if meetup.is_full:
            return Response({'error': 'Meetup is full'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create registration
        registration = Registration.objects.create(user=meetup_user, meetup=meetup)
        
        return Response({
            'message': 'Registration successful',
            'registration_id': registration.id
        }, status=status.HTTP_201_CREATED)
        
    except Meetup.DoesNotExist:
        return Response({'error': 'Meetup not found'}, status=status.HTTP_404_NOT_FOUND)
    except MeetupUser.DoesNotExist:
        return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
def unregister_from_meetup(request, meetup_id):
    if not request.user.is_authenticated:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        meetup = Meetup.objects.get(id=meetup_id)
        meetup_user = request.user.meetup_profile
        
        registration = Registration.objects.get(user=meetup_user, meetup=meetup)
        registration.delete()
        
        return Response({
            'message': 'Unregistration successful'
        }, status=status.HTTP_200_OK)
        
    except Meetup.DoesNotExist:
        return Response({'error': 'Meetup not found'}, status=status.HTTP_404_NOT_FOUND)
    except Registration.DoesNotExist:
        return Response({'error': 'Registration not found'}, status=status.HTTP_404_NOT_FOUND)
    except MeetupUser.DoesNotExist:
        return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)

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
        return Response({'error': 'Meetup not found'}, status=status.HTTP_404_NOT_FOUND)
    except MeetupUser.DoesNotExist:
        return Response({'is_registered': False}, status=status.HTTP_200_OK)

# Admin-specific views
def is_admin_user(request):
    """Helper function to check if user is admin"""
    if not request.user.is_authenticated:
        return False
    try:
        return request.user.meetup_profile.is_admin
    except MeetupUser.DoesNotExist:
        return False

@api_view(['GET'])
def admin_users_list(request):
    """Get all users for admin view"""
    if not is_admin_user(request):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
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
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
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
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        meetup_user = MeetupUser.objects.get(id=user_id)
        
        # Prevent deleting admin users
        if meetup_user.is_admin:
            return Response({'error': 'Cannot delete admin users'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Delete associated Django user if exists
        if meetup_user.user:
            meetup_user.user.delete()
        else:
            meetup_user.delete()
            
        return Response({'message': 'User deleted successfully'}, status=status.HTTP_200_OK)
        
    except MeetupUser.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
def admin_delete_meetup(request, meetup_id):
    """Delete a meetup (admin only)"""
    if not is_admin_user(request):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        meetup = Meetup.objects.get(id=meetup_id)
        meetup.delete()
        return Response({'message': 'Meetup deleted successfully'}, status=status.HTTP_200_OK)
        
    except Meetup.DoesNotExist:
        return Response({'error': 'Meetup not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def admin_toggle_user_admin(request, user_id):
    """Toggle admin status for a user (admin only)"""
    if not is_admin_user(request):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        meetup_user = MeetupUser.objects.get(id=user_id)
        meetup_user.is_admin = not meetup_user.is_admin
        meetup_user.save()
        
        return Response({
            'message': f'User admin status {"enabled" if meetup_user.is_admin else "disabled"}',
            'is_admin': meetup_user.is_admin
        }, status=status.HTTP_200_OK)
        
    except MeetupUser.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def admin_statistics(request):
    """Get dashboard statistics for admin"""
    if not is_admin_user(request):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
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
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        meetup = Meetup.objects.get(id=meetup_id)
        meetup_user = request.user.meetup_profile
        
        # Check if user is the creator of the meetup
        if meetup.creator != meetup_user:
            return Response({'error': 'Only meetup creators can add participants'}, status=status.HTTP_403_FORBIDDEN)
        
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if meetup is full
        if meetup.is_full:
            return Response({'error': 'Meetup is full'}, status=status.HTTP_400_BAD_REQUEST)
        
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
            return Response({'error': 'User is already registered for this meetup'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create registration
        registration = Registration.objects.create(user=participant_user, meetup=meetup)
        
        return Response({
            'message': 'Participant added successfully',
            'participant': {
                'id': participant_user.id,
                'name': participant_user.name,
                'email': participant_user.email,
                'registration_id': registration.id
            }
        }, status=status.HTTP_201_CREATED)
        
    except Meetup.DoesNotExist:
        return Response({'error': 'Meetup not found'}, status=status.HTTP_404_NOT_FOUND)
    except MeetupUser.DoesNotExist:
        return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
def remove_participant(request, meetup_id, registration_id):
    """Remove a participant from meetup (for meetup creators)"""
    if not request.user.is_authenticated:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        meetup = Meetup.objects.get(id=meetup_id)
        meetup_user = request.user.meetup_profile
        
        # Check if user is the creator of the meetup
        if meetup.creator != meetup_user:
            return Response({'error': 'Only meetup creators can remove participants'}, status=status.HTTP_403_FORBIDDEN)
        
        registration = Registration.objects.get(id=registration_id, meetup=meetup)
        registration.delete()
        
        return Response({'message': 'Participant removed successfully'}, status=status.HTTP_200_OK)
        
    except Meetup.DoesNotExist:
        return Response({'error': 'Meetup not found'}, status=status.HTTP_404_NOT_FOUND)
    except Registration.DoesNotExist:
        return Response({'error': 'Registration not found'}, status=status.HTTP_404_NOT_FOUND)
    except MeetupUser.DoesNotExist:
        return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)
