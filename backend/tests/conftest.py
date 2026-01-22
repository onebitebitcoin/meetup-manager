"""
Pytest configuration and fixtures for backend tests.
"""
import uuid

import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from meetups.models import Meetup, MeetupUser, Notification, Registration, Task, TaskSubmission, Waitlist


def _unique_id():
    """Generate a short unique ID for test data."""
    return uuid.uuid4().hex[:8]


@pytest.fixture
def api_client():
    """Return an API client instance."""
    return APIClient()


@pytest.fixture
def create_user(db):
    """Factory fixture for creating Django User."""
    def _create_user(username=None, email=None, password='testpass123'):
        uid = _unique_id()
        if username is None:
            username = f'testuser_{uid}'
        if email is None:
            email = f'test_{uid}@example.com'
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        return user
    return _create_user


@pytest.fixture
def create_meetup_user(db, create_user):
    """Factory fixture for creating MeetupUser."""
    def _create_meetup_user(name=None, email=None, is_admin=False, with_django_user=True):
        uid = _unique_id()
        if name is None:
            name = f'Test User {uid}'
        if email is None:
            email = f'test_{uid}@example.com'

        if with_django_user:
            username = name.lower().replace(' ', '_')[:30] + '_' + uid
            django_user = create_user(username=username, email=email)
            meetup_user = MeetupUser.objects.create(
                user=django_user,
                name=name,
                email=email,
                is_admin=is_admin
            )
        else:
            meetup_user = MeetupUser.objects.create(
                name=name,
                email=email,
                is_admin=is_admin
            )
        return meetup_user
    return _create_meetup_user


@pytest.fixture
def create_meetup(db, create_meetup_user):
    """Factory fixture for creating Meetup."""
    def _create_meetup(
        name=None,
        description='Test Description',
        max_participants=10,
        creator=None,
        **kwargs
    ):
        from datetime import timedelta

        from django.utils import timezone

        uid = _unique_id()
        if name is None:
            name = f'Test Meetup {uid}'
        if creator is None:
            creator = create_meetup_user()

        defaults = {
            'name': name,
            'description': description,
            'date_time': timezone.now() + timedelta(days=7),
            'location': 'Test Location',
            'max_participants': max_participants,
            'creator': creator,
        }
        defaults.update(kwargs)
        return Meetup.objects.create(**defaults)
    return _create_meetup


@pytest.fixture
def create_registration(db):
    """Factory fixture for creating Registration."""
    def _create_registration(user, meetup):
        return Registration.objects.create(user=user, meetup=meetup)
    return _create_registration


@pytest.fixture
def create_waitlist(db):
    """Factory fixture for creating Waitlist."""
    def _create_waitlist(user, meetup, position=None):
        return Waitlist.objects.create(user=user, meetup=meetup, position=position or 1)
    return _create_waitlist


@pytest.fixture
def create_task(db):
    """Factory fixture for creating Task."""
    def _create_task(meetup, title='Test Task', description='Test Description', deadline=None):
        from datetime import timedelta

        from django.utils import timezone

        if deadline is None:
            deadline = timezone.now() + timedelta(days=3)

        return Task.objects.create(
            meetup=meetup,
            title=title,
            description=description,
            deadline=deadline
        )
    return _create_task


@pytest.fixture
def create_submission(db):
    """Factory fixture for creating TaskSubmission."""
    def _create_submission(task, user, message='Test submission', status='pending'):
        return TaskSubmission.objects.create(
            task=task,
            user=user,
            message=message,
            status=status
        )
    return _create_submission


@pytest.fixture
def create_notification(db):
    """Factory fixture for creating Notification."""
    def _create_notification(user, title='Test Notification', message='Test message', meetup=None):
        return Notification.objects.create(
            user=user,
            title=title,
            message=message,
            meetup=meetup,
            notification_type='general'
        )
    return _create_notification


@pytest.fixture
def authenticated_client(api_client, create_user):
    """Return an authenticated API client."""
    def _authenticated_client(is_admin=False):
        uid = _unique_id()
        username = f'authuser_{uid}' if not is_admin else f'adminuser_{uid}'
        email = f'{username}@example.com'

        user = create_user(username=username, email=email, password='testpass123')
        meetup_user = MeetupUser.objects.create(
            user=user,
            name=username,
            email=email,
            is_admin=is_admin
        )

        api_client.force_authenticate(user=user)
        return api_client, user, meetup_user
    return _authenticated_client
