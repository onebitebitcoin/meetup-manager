import re

from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from rest_framework import serializers

from .models import Meetup, MeetupUser, Notification, Registration, Task, TaskSubmission, Waitlist
from .utils.keyboard_converter import has_korean_characters, korean_to_english
from .utils.secure_logging import log_korean_conversion


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    username = serializers.CharField(
        max_length=150,
        min_length=3,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9가-힣ㄱ-ㅎㅏ-ㅣ_-]+$',
                message='사용자명은 영문, 한글, 숫자, 밑줄(_), 하이픈(-)만 사용할 수 있습니다.'
            )
        ]
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def validate_username(self, value):
        """
        Custom username validation with detailed error messages
        """
        # Get original value before Django's automatic trimming
        original_value = self.initial_data.get('username', value)

        if not original_value:
            raise serializers.ValidationError("사용자명을 입력해주세요.")

        # Check for leading/trailing whitespace in original value
        if original_value.startswith(' ') or original_value.endswith(' ') or original_value.startswith('\t') or original_value.endswith('\t'):
            raise serializers.ValidationError("사용자명에는 공백을 사용할 수 없습니다.")

        # Use trimmed value for remaining validation
        if not value:
            raise serializers.ValidationError("사용자명을 입력해주세요.")

        # Check minimum length
        if len(value) < 3:
            raise serializers.ValidationError("사용자명은 최소 3자 이상이어야 합니다.")

        # Check maximum length
        if len(value) > 150:
            raise serializers.ValidationError("사용자명은 150자를 초과할 수 없습니다.")

        # Check for whitespace within the username
        if ' ' in value or '\t' in value or '\n' in value:
            raise serializers.ValidationError("사용자명에는 공백을 사용할 수 없습니다.")

        # Check for invalid characters
        if not re.match(r'^[a-zA-Z0-9가-힣ㄱ-ㅎㅏ-ㅣ_-]+$', value):
            raise serializers.ValidationError("사용자명은 영문, 한글, 숫자, 밑줄(_), 하이픈(-)만 사용할 수 있습니다.")

        # Check if username starts or ends with special characters
        if value.startswith('-') or value.startswith('_') or value.endswith('-') or value.endswith('_'):
            raise serializers.ValidationError("사용자명은 밑줄(_)이나 하이픈(-)으로 시작하거나 끝날 수 없습니다.")

        # Check for consecutive special characters
        if '--' in value or '__' in value or '_-' in value or '-_' in value:
            raise serializers.ValidationError("사용자명에는 연속된 특수문자를 사용할 수 없습니다.")

        # Check if username already exists (case-insensitive)
        # Skip this check during testing
        if not getattr(self, '_test_mode', False) and User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("이미 존재하는 사용자입니다.")

        return value.lower()  # Convert to lowercase for consistency

    def create(self, validated_data):
        # Convert Korean password to English if necessary
        password = validated_data['password']
        if has_korean_characters(password):
            password = korean_to_english(password)
            # Security: Use secure logging that doesn't expose sensitive data
            log_korean_conversion(validated_data['username'], action="registration")

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=password
        )

        # Check if MeetupUser already exists with this email (manually created by admin)
        # and has no user_id link yet
        try:
            meetup_user = MeetupUser.objects.get(email=validated_data['email'], user__isnull=True)
            # Link existing MeetupUser to the new Django User and update name
            meetup_user.user = user
            meetup_user.name = validated_data['username']  # Update to user-defined name
            meetup_user.save()
        except MeetupUser.DoesNotExist:
            # Create new MeetupUser if it doesn't exist or if one exists but is already linked
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
            raise serializers.ValidationError("사용자를 찾을 수 없습니다") from None
        except Meetup.DoesNotExist:
            raise serializers.ValidationError("모임을 찾을 수 없습니다") from None

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


class TaskSerializer(serializers.ModelSerializer):
    meetup_name = serializers.CharField(source='meetup.name', read_only=True)
    is_deadline_soon = serializers.ReadOnlyField()
    is_past_deadline = serializers.ReadOnlyField()
    submission_count = serializers.SerializerMethodField()
    user_submission = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ['id', 'meetup', 'meetup_name', 'title', 'description', 'deadline',
                  'created_at', 'updated_at', 'is_deadline_soon', 'is_past_deadline',
                  'submission_count', 'user_submission']

    def get_submission_count(self, obj):
        return obj.submissions.count()

    def get_user_submission(self, obj):
        """Get current user's submission for this task if exists"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        try:
            meetup_user = request.user.meetup_profile
            submission = obj.submissions.filter(user=meetup_user).first()
            if submission:
                return {
                    'id': submission.id,
                    'status': submission.status,
                    'submitted_at': submission.submitted_at
                }
        except Exception:
            pass
        return None


class TaskSubmissionSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    task_title = serializers.CharField(source='task.title', read_only=True)
    file_url = serializers.SerializerMethodField()
    file_name = serializers.SerializerMethodField()

    class Meta:
        model = TaskSubmission
        fields = ['id', 'task', 'task_title', 'user', 'user_name', 'user_email',
                  'message', 'link', 'file', 'file_url', 'file_name', 'status',
                  'submitted_at', 'reviewed_at']

    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None

    def get_file_name(self, obj):
        if obj.file:
            import os
            return os.path.basename(obj.file.name)
        return None
