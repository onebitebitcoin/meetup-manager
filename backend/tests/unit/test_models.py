"""
Unit tests for Django models.
"""
from datetime import timedelta

import pytest
from django.utils import timezone

from meetups.models import Registration, Waitlist


@pytest.mark.django_db
class TestMeetupModel:
    """Tests for Meetup model."""

    def test_meetup_str(self, create_meetup):
        """Test Meetup __str__ method."""
        meetup = create_meetup(name='Test Meetup')
        assert str(meetup) == 'Test Meetup'

    def test_is_full_property_false(self, create_meetup):
        """Test is_full returns False when not full."""
        meetup = create_meetup(max_participants=10)
        meetup.current_participants = 5
        meetup.save()
        assert meetup.is_full is False

    def test_is_full_property_true(self, create_meetup):
        """Test is_full returns True when full."""
        meetup = create_meetup(max_participants=10)
        meetup.current_participants = 10
        meetup.save()
        assert meetup.is_full is True

    def test_available_spots(self, create_meetup):
        """Test available_spots calculation."""
        meetup = create_meetup(max_participants=10)
        meetup.current_participants = 3
        meetup.save()
        assert meetup.available_spots == 7

    def test_hashtags_list_property(self, create_meetup):
        """Test hashtags_list returns correct list."""
        meetup = create_meetup()
        meetup.hashtags = '#python,#django,#meetup'
        meetup.save()

        hashtags = meetup.hashtags_list
        assert len(hashtags) == 3
        assert '#python' in hashtags
        assert '#django' in hashtags
        assert '#meetup' in hashtags

    def test_hashtags_list_empty(self, create_meetup):
        """Test hashtags_list returns empty list when no hashtags."""
        meetup = create_meetup()
        meetup.hashtags = None
        meetup.save()
        assert meetup.hashtags_list == []

    def test_add_hashtag(self, create_meetup):
        """Test adding hashtag to meetup."""
        meetup = create_meetup()
        meetup.hashtags = '#existing'
        meetup.add_hashtag('new')
        assert '#new' in meetup.hashtags_list

    def test_add_hashtag_with_hash(self, create_meetup):
        """Test adding hashtag that already has # prefix."""
        meetup = create_meetup()
        meetup.hashtags = None
        meetup.add_hashtag('#newtag')
        assert '#newtag' in meetup.hashtags_list

    def test_remove_hashtag(self, create_meetup):
        """Test removing hashtag from meetup."""
        meetup = create_meetup()
        meetup.hashtags = '#tag1,#tag2,#tag3'
        meetup.remove_hashtag('#tag2')
        assert '#tag2' not in meetup.hashtags_list
        assert '#tag1' in meetup.hashtags_list
        assert '#tag3' in meetup.hashtags_list

    def test_image_display_url_with_image_url(self, create_meetup):
        """Test image_display_url returns image_url when set."""
        meetup = create_meetup()
        meetup.image_url = 'https://example.com/image.jpg'
        assert meetup.image_display_url == 'https://example.com/image.jpg'


@pytest.mark.django_db
class TestRegistrationModel:
    """Tests for Registration model."""

    def test_registration_str(self, create_meetup_user, create_meetup, create_registration):
        """Test Registration __str__ method."""
        user = create_meetup_user(name='John', email='john@example.com')
        meetup = create_meetup(name='My Meetup')
        registration = create_registration(user, meetup)
        assert 'John' in str(registration)
        assert 'My Meetup' in str(registration)

    def test_registration_increases_participant_count(self, create_meetup_user, create_meetup):
        """Test that registration increases current_participants."""
        meetup = create_meetup(max_participants=10)
        initial_count = meetup.current_participants

        user = create_meetup_user(name='Participant', email='participant@example.com')
        Registration.objects.create(user=user, meetup=meetup)

        meetup.refresh_from_db()
        assert meetup.current_participants == initial_count + 1

    def test_registration_delete_decreases_participant_count(self, create_meetup_user, create_meetup, create_registration):
        """Test that deleting registration decreases current_participants."""
        meetup = create_meetup(max_participants=10)
        user = create_meetup_user(name='Participant', email='participant@example.com')
        registration = create_registration(user, meetup)

        meetup.refresh_from_db()
        count_after_registration = meetup.current_participants

        registration.delete()
        meetup.refresh_from_db()
        assert meetup.current_participants == count_after_registration - 1


@pytest.mark.django_db
class TestWaitlistModel:
    """Tests for Waitlist model."""

    def test_waitlist_str(self, create_meetup_user, create_meetup, create_waitlist):
        """Test Waitlist __str__ method."""
        user = create_meetup_user(name='Waiter', email='waiter@example.com')
        meetup = create_meetup(name='Full Meetup')
        waitlist = create_waitlist(user, meetup, position=3)
        assert 'Waiter' in str(waitlist)
        assert 'Full Meetup' in str(waitlist)
        assert '3' in str(waitlist)

    def test_waitlist_auto_position(self, create_meetup_user, create_meetup):
        """Test that position is auto-assigned."""
        meetup = create_meetup()

        user1 = create_meetup_user(name='User1', email='user1@example.com')
        waitlist1 = Waitlist.objects.create(user=user1, meetup=meetup)
        assert waitlist1.position == 1

        user2 = create_meetup_user(name='User2', email='user2@example.com')
        waitlist2 = Waitlist.objects.create(user=user2, meetup=meetup)
        assert waitlist2.position == 2

    def test_waitlist_delete_adjusts_positions(self, create_meetup_user, create_meetup):
        """Test that deleting waitlist entry adjusts positions."""
        meetup = create_meetup()

        user1 = create_meetup_user(name='User1', email='user1@example.com')
        user2 = create_meetup_user(name='User2', email='user2@example.com')
        user3 = create_meetup_user(name='User3', email='user3@example.com')

        waitlist1 = Waitlist.objects.create(user=user1, meetup=meetup)
        waitlist2 = Waitlist.objects.create(user=user2, meetup=meetup)
        waitlist3 = Waitlist.objects.create(user=user3, meetup=meetup)

        waitlist1.delete()

        waitlist2.refresh_from_db()
        waitlist3.refresh_from_db()

        assert waitlist2.position == 1
        assert waitlist3.position == 2


@pytest.mark.django_db
class TestTaskModel:
    """Tests for Task model."""

    def test_task_str(self, create_meetup, create_task):
        """Test Task __str__ method."""
        meetup = create_meetup(name='Study Group')
        task = create_task(meetup, title='Read Chapter 1')
        assert 'Read Chapter 1' in str(task)
        assert 'Study Group' in str(task)

    def test_is_deadline_soon_true(self, create_meetup, create_task):
        """Test is_deadline_soon returns True within 3 days."""
        meetup = create_meetup()
        task = create_task(meetup, deadline=timezone.now() + timedelta(days=2))
        assert task.is_deadline_soon is True

    def test_is_deadline_soon_false(self, create_meetup, create_task):
        """Test is_deadline_soon returns False after 3 days."""
        meetup = create_meetup()
        task = create_task(meetup, deadline=timezone.now() + timedelta(days=5))
        assert task.is_deadline_soon is False

    def test_is_past_deadline_true(self, create_meetup, create_task):
        """Test is_past_deadline returns True when passed."""
        meetup = create_meetup()
        task = create_task(meetup, deadline=timezone.now() - timedelta(days=1))
        assert task.is_past_deadline is True

    def test_is_past_deadline_false(self, create_meetup, create_task):
        """Test is_past_deadline returns False when not passed."""
        meetup = create_meetup()
        task = create_task(meetup, deadline=timezone.now() + timedelta(days=1))
        assert task.is_past_deadline is False
