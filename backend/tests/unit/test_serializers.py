"""
Unit tests for Django REST Framework serializers.
"""
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
