from rest_framework import serializers
from django.contrib.auth.models import User
from .models import MeetupUser, Meetup, Registration, Waitlist, Notification

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        
        # Check if MeetupUser already exists with this email (manually created by admin)
        try:
            meetup_user = MeetupUser.objects.get(email=validated_data['email'])
            # Link existing MeetupUser to the new Django User
            meetup_user.user = user
            meetup_user.save()
        except MeetupUser.DoesNotExist:
            # Create new MeetupUser if it doesn't exist
            meetup_user = MeetupUser.objects.create(
                user=user,
                name=validated_data['username'],  # Use username as name
                email=validated_data['email'],
                phone=''
            )
        
        return user

class MeetupUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    total_meetups_created = serializers.SerializerMethodField()
    
    class Meta:
        model = MeetupUser
        fields = ['id', 'name', 'email', 'phone', 'is_admin', 'created_at', 'username', 'total_meetups_created']
    
    def get_total_meetups_created(self, obj):
        return obj.created_meetups.count()

class MeetupSerializer(serializers.ModelSerializer):
    is_full = serializers.ReadOnlyField()
    available_spots = serializers.ReadOnlyField()
    creator_name = serializers.CharField(source='creator.name', read_only=True)
    creator_email = serializers.CharField(source='creator.email', read_only=True)
    image_display_url = serializers.SerializerMethodField()
    hashtags_list = serializers.ReadOnlyField()
    
    class Meta:
        model = Meetup
        fields = ['id', 'name', 'description', 'date_time', 'end_time', 'location', 
                 'max_participants', 'current_participants', 'created_at',
                 'is_full', 'available_spots', 'creator', 'creator_name', 'creator_email',
                 'image', 'image_url', 'image_display_url', 'hashtags', 'hashtags_list']
    
    def get_image_display_url(self, obj):
        """Return the full image URL - either from uploaded file or external URL"""
        if obj.image:
            # Build absolute URL for uploaded images
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            # Fallback: use SITE_URL from settings or just relative URL
            from django.conf import settings
            site_url = getattr(settings, 'SITE_URL', '')
            if site_url:
                return f"{site_url.rstrip('/')}{obj.image.url}"
            return obj.image.url  # Return relative URL as fallback
        elif obj.image_url:
            return obj.image_url
        return ''

    def validate(self, attrs):
        hashtags = attrs.get('hashtags')
        if hashtags:
            parts = [p.strip() for p in hashtags.split(',') if p.strip()]
            if len(parts) > 5:
                raise serializers.ValidationError({'hashtags': '해시태그는 최대 5개까지 입력할 수 있습니다.'})
        return attrs

class RegistrationSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    meetup_name = serializers.CharField(source='meetup.name', read_only=True)
    meetup_date_time = serializers.DateTimeField(source='meetup.date_time', read_only=True)
    
    class Meta:
        model = Registration
        fields = ['id', 'user', 'meetup', 'registered_at', 
                 'user_name', 'user_email', 'meetup_name', 'meetup_date_time']

class RegisterUserSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    meetup_id = serializers.IntegerField()
    
    def validate(self, data):
        try:
            user = MeetupUser.objects.get(id=data['user_id'])
            meetup = Meetup.objects.get(id=data['meetup_id'])
        except MeetupUser.DoesNotExist:
            raise serializers.ValidationError("사용자를 찾을 수 없습니다")
        except Meetup.DoesNotExist:
            raise serializers.ValidationError("모임을 찾을 수 없습니다")
        
        if Registration.objects.filter(user=user, meetup=meetup).exists():
            raise serializers.ValidationError("이미 이 모임에 신청되어 있습니다")
        
        if meetup.is_full:
            raise serializers.ValidationError("모임 정원이 가득 찼습니다")
        
        data['user'] = user
        data['meetup'] = meetup
        return data


class WaitlistSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    meetup_name = serializers.CharField(source='meetup.name', read_only=True)
    meetup_date_time = serializers.DateTimeField(source='meetup.date_time', read_only=True)
    
    class Meta:
        model = Waitlist
        fields = ['id', 'user', 'meetup', 'position', 'waitlisted_at',
                 'user_name', 'user_email', 'meetup_name', 'meetup_date_time']


class NotificationSerializer(serializers.ModelSerializer):
    meetup_name = serializers.CharField(source='meetup.name', read_only=True)
    time_ago = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'notification_type', 'meetup', 'meetup_name', 
                 'is_read', 'created_at', 'time_ago']
    
    def get_time_ago(self, obj):
        """Get human-readable time difference"""
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        diff = now - obj.created_at
        
        if diff.days > 0:
            return f"{diff.days}일 전"
        elif diff.seconds >= 3600:
            hours = diff.seconds // 3600
            return f"{hours}시간 전"
        elif diff.seconds >= 60:
            minutes = diff.seconds // 60
            return f"{minutes}분 전"
        else:
            return "방금 전"
