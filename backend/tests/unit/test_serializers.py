"""
Unit tests for Django REST Framework serializers.
"""
import uuid
from datetime import timedelta

import pytest
from django.utils import timezone

from meetups.serializers import (
    MeetupSerializer,
    MeetupUserSerializer,
    TaskSerializer,
    UserRegistrationSerializer,
)


@pytest.mark.django_db
class TestUserRegistrationSerializer:
    """Tests for UserRegistrationSerializer."""

    def test_valid_registration_data(self):
        """Test serializer accepts valid data."""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'securepass123'
        }
        serializer = UserRegistrationSerializer(data=data)
        serializer._test_mode = True  # Skip unique check
        assert serializer.is_valid(), serializer.errors

    def test_invalid_username_too_short(self):
        """Test serializer rejects short username."""
        data = {
            'username': 'ab',
            'email': 'user@example.com',
            'password': 'securepass123'
        }
        serializer = UserRegistrationSerializer(data=data)
        serializer._test_mode = True
        assert not serializer.is_valid()
        assert 'username' in serializer.errors

    def test_invalid_username_with_spaces(self):
        """Test serializer rejects username with spaces."""
        data = {
            'username': 'user name',
            'email': 'user@example.com',
            'password': 'securepass123'
        }
        serializer = UserRegistrationSerializer(data=data)
        serializer._test_mode = True
        assert not serializer.is_valid()
        assert 'username' in serializer.errors

    def test_invalid_username_special_chars(self):
        """Test serializer rejects username with invalid characters."""
        data = {
            'username': 'user@name!',
            'email': 'user@example.com',
            'password': 'securepass123'
        }
        serializer = UserRegistrationSerializer(data=data)
        serializer._test_mode = True
        assert not serializer.is_valid()
        assert 'username' in serializer.errors

    def test_username_converted_to_lowercase(self):
        """Test username is converted to lowercase."""
        data = {
            'username': 'TestUser',
            'email': 'user@example.com',
            'password': 'securepass123'
        }
        serializer = UserRegistrationSerializer(data=data)
        serializer._test_mode = True
        assert serializer.is_valid(), serializer.errors
        assert serializer.validated_data['username'] == 'testuser'


@pytest.mark.django_db
class TestMeetupSerializer:
    """Tests for MeetupSerializer."""

    def test_serializer_output(self, create_meetup):
        """Test serializer correctly serializes meetup."""
        meetup = create_meetup(
            name='Django Meetup',
            description='Learn Django',
            max_participants=20
        )
        serializer = MeetupSerializer(meetup)
        data = serializer.data

        assert data['name'] == 'Django Meetup'
        assert data['description'] == 'Learn Django'
        assert data['max_participants'] == 20
        assert 'is_full' in data
        assert 'available_spots' in data

    def test_serializer_is_full_field(self, create_meetup):
        """Test is_full computed field."""
        meetup = create_meetup(max_participants=5)
        meetup.current_participants = 5
        meetup.save()

        serializer = MeetupSerializer(meetup)
        assert serializer.data['is_full'] is True

    def test_serializer_available_spots_field(self, create_meetup):
        """Test available_spots computed field."""
        meetup = create_meetup(max_participants=10)
        meetup.current_participants = 3
        meetup.save()

        serializer = MeetupSerializer(meetup)
        assert serializer.data['available_spots'] == 7

    def test_hashtags_validation_max_five(self, create_meetup_user):
        """Test hashtags validation rejects more than 5 tags."""
        creator = create_meetup_user()
        data = {
            'name': 'Test',
            'description': 'Test',
            'date_time': timezone.now() + timedelta(days=1),
            'location': 'Test Location',
            'max_participants': 10,
            'creator': creator.id,
            'hashtags': '#1,#2,#3,#4,#5,#6'
        }
        serializer = MeetupSerializer(data=data)
        assert not serializer.is_valid()
        assert 'hashtags' in serializer.errors


@pytest.mark.django_db
class TestMeetupUserSerializer:
    """Tests for MeetupUserSerializer."""

    def test_serializer_output(self, create_meetup_user):
        """Test serializer correctly serializes meetup user."""
        user = create_meetup_user(
            name='John Doe',
            email='john@example.com',
            is_admin=True
        )
        serializer = MeetupUserSerializer(user)
        data = serializer.data

        assert data['name'] == 'John Doe'
        assert data['email'] == 'john@example.com'
        assert data['is_admin'] is True

    def test_total_meetups_created_field(self, create_meetup_user, create_meetup):
        """Test total_meetups_created computed field."""
        creator = create_meetup_user(name='Creator', email='creator@example.com')
        create_meetup(name='Meetup 1', creator=creator)
        create_meetup(name='Meetup 2', creator=creator)

        serializer = MeetupUserSerializer(creator)
        assert serializer.data['total_meetups_created'] == 2


@pytest.mark.django_db
class TestTaskSerializer:
    """Tests for TaskSerializer."""

    def test_serializer_output(self, create_meetup, create_task):
        """Test serializer correctly serializes task."""
        meetup = create_meetup(name='Study Group')
        task = create_task(meetup, title='Read Chapter 1', description='Read and summarize')

        serializer = TaskSerializer(task)
        data = serializer.data

        assert data['title'] == 'Read Chapter 1'
        assert data['description'] == 'Read and summarize'
        assert data['meetup_name'] == 'Study Group'

    def test_is_deadline_soon_field(self, create_meetup, create_task):
        """Test is_deadline_soon computed field."""
        meetup = create_meetup()
        task = create_task(meetup, deadline=timezone.now() + timedelta(days=2))

        serializer = TaskSerializer(task)
        assert serializer.data['is_deadline_soon'] is True

    def test_is_past_deadline_field(self, create_meetup, create_task):
        """Test is_past_deadline computed field."""
        meetup = create_meetup()
        task = create_task(meetup, deadline=timezone.now() - timedelta(days=1))

        serializer = TaskSerializer(task)
        assert serializer.data['is_past_deadline'] is True


@pytest.mark.django_db
class TestValidateUsernameValue:

    def test_valid_username_returned_lowercase(self):
        from meetups.serializers import validate_username_value
        assert validate_username_value('TestUser') == 'testuser'

    def test_empty_original_value_raises(self):
        from rest_framework import serializers as drf_serializers

        from meetups.serializers import validate_username_value
        with pytest.raises(drf_serializers.ValidationError):
            validate_username_value('', original_value='')

    def test_leading_space_raises(self):
        from rest_framework import serializers as drf_serializers

        from meetups.serializers import validate_username_value
        with pytest.raises(drf_serializers.ValidationError, match='공백'):
            validate_username_value('test', original_value=' test')

    def test_trailing_space_raises(self):
        from rest_framework import serializers as drf_serializers

        from meetups.serializers import validate_username_value
        with pytest.raises(drf_serializers.ValidationError, match='공백'):
            validate_username_value('test', original_value='test ')

    def test_too_short_raises(self):
        from rest_framework import serializers as drf_serializers

        from meetups.serializers import validate_username_value
        with pytest.raises(drf_serializers.ValidationError, match='3자'):
            validate_username_value('ab')

    def test_too_long_raises(self):
        from rest_framework import serializers as drf_serializers

        from meetups.serializers import validate_username_value
        with pytest.raises(drf_serializers.ValidationError, match='150자'):
            validate_username_value('a' * 151)

    def test_internal_space_raises(self):
        from rest_framework import serializers as drf_serializers

        from meetups.serializers import validate_username_value
        with pytest.raises(drf_serializers.ValidationError, match='공백'):
            validate_username_value('user name')

    def test_invalid_chars_raises(self):
        from rest_framework import serializers as drf_serializers

        from meetups.serializers import validate_username_value
        with pytest.raises(drf_serializers.ValidationError):
            validate_username_value('user@name!')

    def test_starts_with_dash_raises(self):
        from rest_framework import serializers as drf_serializers

        from meetups.serializers import validate_username_value
        with pytest.raises(drf_serializers.ValidationError, match='시작하거나 끝날 수'):
            validate_username_value('-username')

    def test_ends_with_underscore_raises(self):
        from rest_framework import serializers as drf_serializers

        from meetups.serializers import validate_username_value
        with pytest.raises(drf_serializers.ValidationError, match='시작하거나 끝날 수'):
            validate_username_value('username_')

    def test_consecutive_dashes_raises(self):
        from rest_framework import serializers as drf_serializers

        from meetups.serializers import validate_username_value
        with pytest.raises(drf_serializers.ValidationError, match='연속된'):
            validate_username_value('user--name')

    def test_double_underscore_raises(self):
        from rest_framework import serializers as drf_serializers

        from meetups.serializers import validate_username_value
        with pytest.raises(drf_serializers.ValidationError, match='연속된'):
            validate_username_value('user__name')

    def test_duplicate_username_raises(self):
        from django.contrib.auth.models import User
        from rest_framework import serializers as drf_serializers

        from meetups.serializers import validate_username_value
        User.objects.create_user(username='taken_user', password='pass')
        with pytest.raises(drf_serializers.ValidationError, match='이미 존재'):
            validate_username_value('taken_user')

    def test_exclude_user_id_allows_own_username(self):
        from django.contrib.auth.models import User

        from meetups.serializers import validate_username_value
        user = User.objects.create_user(username='myuser', password='pass')
        result = validate_username_value('myuser', exclude_user_id=user.id)
        assert result == 'myuser'

    def test_korean_username_valid(self):
        from meetups.serializers import validate_username_value
        result = validate_username_value('한글유저')
        assert result == '한글유저'


@pytest.mark.django_db
class TestRegisterUserSerializer:

    def test_validate_success(self, create_meetup_user, create_meetup):
        from meetups.serializers import RegisterUserSerializer
        user = create_meetup_user(name='RegUser', email='reguser@example.com')
        meetup = create_meetup()
        serializer = RegisterUserSerializer(data={'user_id': user.id, 'meetup_id': meetup.id})
        assert serializer.is_valid(), serializer.errors
        assert serializer.validated_data['user'] == user
        assert serializer.validated_data['meetup'] == meetup

    def test_validate_user_not_found(self, create_meetup):
        from meetups.serializers import RegisterUserSerializer
        meetup = create_meetup()
        serializer = RegisterUserSerializer(data={'user_id': 99999, 'meetup_id': meetup.id})
        assert not serializer.is_valid()

    def test_validate_meetup_not_found(self, create_meetup_user):
        from meetups.serializers import RegisterUserSerializer
        user = create_meetup_user()
        serializer = RegisterUserSerializer(data={'user_id': user.id, 'meetup_id': 99999})
        assert not serializer.is_valid()

    def test_validate_already_registered(self, create_meetup_user, create_meetup, create_registration):
        from meetups.serializers import RegisterUserSerializer
        user = create_meetup_user(name='AlreadyReg', email='alreadyreg@example.com')
        meetup = create_meetup()
        create_registration(user, meetup)
        serializer = RegisterUserSerializer(data={'user_id': user.id, 'meetup_id': meetup.id})
        assert not serializer.is_valid()

    def test_validate_meetup_full(self, create_meetup_user, create_meetup, create_registration):
        from meetups.serializers import RegisterUserSerializer
        meetup = create_meetup(max_participants=1)
        filler = create_meetup_user(name='Filler', email='filler@example.com')
        create_registration(filler, meetup)
        user = create_meetup_user(name='Blocked', email='blocked@example.com')
        serializer = RegisterUserSerializer(data={'user_id': user.id, 'meetup_id': meetup.id})
        assert not serializer.is_valid()


@pytest.mark.django_db
class TestNotificationSerializerTimeAgo:

    def _make_notification(self, create_meetup_user, create_notification, delta):
        user = create_meetup_user(name='NotifUser', email=f'notif_{uuid.uuid4().hex[:6]}@example.com')
        notif = create_notification(user, title='Test')
        from meetups.models import Notification
        Notification.objects.filter(id=notif.id).update(created_at=timezone.now() - delta)
        notif.refresh_from_db()
        return notif

    def test_days_ago(self, create_meetup_user, create_notification):
        from meetups.serializers import NotificationSerializer
        notif = self._make_notification(create_meetup_user, create_notification, timedelta(days=3))
        assert '일 전' in NotificationSerializer(notif).data['time_ago']

    def test_hours_ago(self, create_meetup_user, create_notification):
        from meetups.serializers import NotificationSerializer
        notif = self._make_notification(create_meetup_user, create_notification, timedelta(hours=5))
        assert '시간 전' in NotificationSerializer(notif).data['time_ago']

    def test_minutes_ago(self, create_meetup_user, create_notification):
        from meetups.serializers import NotificationSerializer
        notif = self._make_notification(create_meetup_user, create_notification, timedelta(minutes=30))
        assert '분 전' in NotificationSerializer(notif).data['time_ago']

    def test_just_now(self, create_meetup_user, create_notification):
        from meetups.serializers import NotificationSerializer
        notif = self._make_notification(create_meetup_user, create_notification, timedelta(seconds=10))
        assert NotificationSerializer(notif).data['time_ago'] == '방금 전'


@pytest.mark.django_db
class TestReviewSerializerTimeAgo:

    def _make_review(self, create_meetup, create_meetup_user, create_registration, delta):
        past = timezone.now() - timedelta(hours=3)
        meetup = create_meetup(date_time=past - timedelta(hours=2), end_time=past)
        user = create_meetup_user(name='RevUser', email=f'rev_{uuid.uuid4().hex[:6]}@example.com')
        create_registration(user, meetup)
        from meetups.models import Review
        review = Review.objects.create(meetup=meetup, user=user, rating=5, content='test')
        Review.objects.filter(id=review.id).update(created_at=timezone.now() - delta)
        review.refresh_from_db()
        return review

    def test_days_ago(self, create_meetup, create_meetup_user, create_registration):
        from meetups.serializers import ReviewSerializer
        review = self._make_review(create_meetup, create_meetup_user, create_registration, timedelta(days=2))
        assert '일 전' in ReviewSerializer(review).data['time_ago']

    def test_hours_ago(self, create_meetup, create_meetup_user, create_registration):
        from meetups.serializers import ReviewSerializer
        review = self._make_review(create_meetup, create_meetup_user, create_registration, timedelta(hours=4))
        assert '시간 전' in ReviewSerializer(review).data['time_ago']

    def test_minutes_ago(self, create_meetup, create_meetup_user, create_registration):
        from meetups.serializers import ReviewSerializer
        review = self._make_review(create_meetup, create_meetup_user, create_registration, timedelta(minutes=20))
        assert '분 전' in ReviewSerializer(review).data['time_ago']

    def test_just_now(self, create_meetup, create_meetup_user, create_registration):
        from meetups.serializers import ReviewSerializer
        review = self._make_review(create_meetup, create_meetup_user, create_registration, timedelta(seconds=5))
        assert ReviewSerializer(review).data['time_ago'] == '방금 전'

    def test_image_url_fallback(self, create_meetup, create_meetup_user, create_registration):
        from meetups.serializers import ReviewSerializer
        past = timezone.now() - timedelta(hours=3)
        meetup = create_meetup(date_time=past - timedelta(hours=2), end_time=past,
                               image_url='https://example.com/img.jpg')
        user = create_meetup_user(name='ImgUser', email=f'img_{uuid.uuid4().hex[:6]}@example.com')
        create_registration(user, meetup)
        from meetups.models import Review
        review = Review.objects.create(meetup=meetup, user=user, rating=4, content='img test')
        assert ReviewSerializer(review).data['meetup_image_url'] == 'https://example.com/img.jpg'

    def test_no_image_returns_none(self, create_meetup, create_meetup_user, create_registration):
        from meetups.serializers import ReviewSerializer
        past = timezone.now() - timedelta(hours=3)
        meetup = create_meetup(date_time=past - timedelta(hours=2), end_time=past)
        user = create_meetup_user(name='NoImgUser', email=f'noimg_{uuid.uuid4().hex[:6]}@example.com')
        create_registration(user, meetup)
        from meetups.models import Review
        review = Review.objects.create(meetup=meetup, user=user, rating=3, content='no img')
        assert ReviewSerializer(review).data['meetup_image_url'] is None


@pytest.mark.django_db
class TestUserRegistrationSerializerCreate:

    def test_regular_password_creates_user(self):
        from meetups.serializers import UserRegistrationSerializer
        data = {'username': 'normaluser', 'email': 'normal@example.com', 'password': 'securepass123'}
        serializer = UserRegistrationSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        user = serializer.save()
        assert user.username == 'normaluser'

    def test_existing_guest_meetupuser_linked_on_register(self):
        from meetups.models import MeetupUser
        from meetups.serializers import UserRegistrationSerializer
        MeetupUser.objects.create(name='guest', email='guest_link@example.com')
        data = {'username': 'guestlinked', 'email': 'guest_link@example.com', 'password': 'securepass123'}
        serializer = UserRegistrationSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        user = serializer.save()
        guest = MeetupUser.objects.get(email='guest_link@example.com')
        assert guest.user == user
