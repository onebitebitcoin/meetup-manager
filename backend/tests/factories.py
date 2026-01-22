"""
Factory classes for generating test data using factory_boy.
"""
from datetime import timedelta

import factory
from django.contrib.auth.models import User
from django.utils import timezone
from factory.django import DjangoModelFactory

from meetups.models import Meetup, MeetupUser, Notification, Registration, Task, TaskSubmission, Waitlist


class UserFactory(DjangoModelFactory):
    """Factory for Django User model."""
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')


class MeetupUserFactory(DjangoModelFactory):
    """Factory for MeetupUser model."""
    class Meta:
        model = MeetupUser

    user = factory.SubFactory(UserFactory)
    name = factory.LazyAttribute(lambda obj: obj.user.username)
    email = factory.LazyAttribute(lambda obj: obj.user.email)
    phone = factory.Faker('phone_number')
    is_admin = False


class MeetupFactory(DjangoModelFactory):
    """Factory for Meetup model."""
    class Meta:
        model = Meetup

    name = factory.Sequence(lambda n: f'Meetup {n}')
    description = factory.Faker('paragraph')
    date_time = factory.LazyFunction(lambda: timezone.now() + timedelta(days=7))
    end_time = factory.LazyAttribute(lambda obj: obj.date_time + timedelta(hours=2))
    location = factory.Faker('address')
    max_participants = 10
    current_participants = 0
    creator = factory.SubFactory(MeetupUserFactory)
    hashtags = '#test,#meetup'


class RegistrationFactory(DjangoModelFactory):
    """Factory for Registration model."""
    class Meta:
        model = Registration

    user = factory.SubFactory(MeetupUserFactory)
    meetup = factory.SubFactory(MeetupFactory)


class WaitlistFactory(DjangoModelFactory):
    """Factory for Waitlist model."""
    class Meta:
        model = Waitlist

    user = factory.SubFactory(MeetupUserFactory)
    meetup = factory.SubFactory(MeetupFactory)
    position = factory.Sequence(lambda n: n + 1)


class TaskFactory(DjangoModelFactory):
    """Factory for Task model."""
    class Meta:
        model = Task

    meetup = factory.SubFactory(MeetupFactory)
    title = factory.Sequence(lambda n: f'Task {n}')
    description = factory.Faker('paragraph')
    deadline = factory.LazyFunction(lambda: timezone.now() + timedelta(days=3))


class TaskSubmissionFactory(DjangoModelFactory):
    """Factory for TaskSubmission model."""
    class Meta:
        model = TaskSubmission

    task = factory.SubFactory(TaskFactory)
    user = factory.SubFactory(MeetupUserFactory)
    message = factory.Faker('paragraph')
    link = factory.Faker('url')
    status = 'pending'


class NotificationFactory(DjangoModelFactory):
    """Factory for Notification model."""
    class Meta:
        model = Notification

    user = factory.SubFactory(MeetupUserFactory)
    title = factory.Sequence(lambda n: f'Notification {n}')
    message = factory.Faker('paragraph')
    notification_type = 'general'
    is_read = False
