"""
Integration tests for waitlist API endpoints.
"""
import pytest
from django.urls import reverse

from meetups.models import Waitlist


@pytest.mark.django_db
class TestWaitlistAPI:
    """Tests for waitlist endpoints."""

    def test_add_to_waitlist(self, authenticated_client, create_meetup):
        """Test adding to waitlist."""
        client, user, meetup_user = authenticated_client()
        meetup = create_meetup(max_participants=1)
        meetup.current_participants = 1
        meetup.save()

        url = reverse('add-to-waitlist', kwargs={'meetup_id': meetup.id})
        response = client.post(url)

        assert response.status_code == 201
        assert Waitlist.objects.filter(user=meetup_user, meetup=meetup).exists()

    def test_add_to_waitlist_already_registered(self, authenticated_client, create_meetup, create_registration):
        """Test adding to waitlist when already registered fails."""
        client, user, meetup_user = authenticated_client()
        meetup = create_meetup(max_participants=10)
        create_registration(meetup_user, meetup)

        url = reverse('add-to-waitlist', kwargs={'meetup_id': meetup.id})
        response = client.post(url)

        assert response.status_code == 400

    def test_remove_from_waitlist(self, authenticated_client, create_meetup, create_waitlist):
        """Test removing from waitlist."""
        client, user, meetup_user = authenticated_client()
        meetup = create_meetup()
        create_waitlist(meetup_user, meetup)

        url = reverse('remove-from-waitlist', kwargs={'meetup_id': meetup.id})
        response = client.delete(url)

        assert response.status_code == 200
        assert not Waitlist.objects.filter(user=meetup_user, meetup=meetup).exists()

    def test_check_waitlist_status_on_waitlist(self, authenticated_client, create_meetup, create_waitlist):
        """Test checking waitlist status when on waitlist."""
        client, user, meetup_user = authenticated_client()
        meetup = create_meetup()
        create_waitlist(meetup_user, meetup, position=3)

        url = reverse('check-waitlist-status', kwargs={'meetup_id': meetup.id})
        response = client.get(url)

        assert response.status_code == 200
        assert response.data['is_waitlisted'] is True
        assert response.data['position'] == 3

    def test_check_waitlist_status_not_on_waitlist(self, authenticated_client, create_meetup):
        """Test checking waitlist status when not on waitlist."""
        client, user, meetup_user = authenticated_client()
        meetup = create_meetup()

        url = reverse('check-waitlist-status', kwargs={'meetup_id': meetup.id})
        response = client.get(url)

        assert response.status_code == 200
        assert response.data['is_waitlisted'] is False

    def test_get_meetup_waitlist(self, api_client, create_meetup, create_meetup_user, create_waitlist):
        """Test getting meetup waitlist."""
        meetup = create_meetup()
        user1 = create_meetup_user(name='User1', email='user1@example.com')
        user2 = create_meetup_user(name='User2', email='user2@example.com')
        create_waitlist(user1, meetup, position=1)
        create_waitlist(user2, meetup, position=2)

        url = reverse('meetup-waitlist', kwargs={'meetup_id': meetup.id})
        response = api_client.get(url)

        assert response.status_code == 200
        assert len(response.data) == 2

    def test_get_user_waitlists(self, authenticated_client, create_meetup, create_waitlist):
        """Test getting user's waitlists."""
        client, user, meetup_user = authenticated_client()
        meetup1 = create_meetup(name='Meetup 1')
        meetup2 = create_meetup(name='Meetup 2')
        create_waitlist(meetup_user, meetup1)
        create_waitlist(meetup_user, meetup2)

        url = reverse('user-waitlists')
        response = client.get(url)

        assert response.status_code == 200
        assert len(response.data) == 2


@pytest.mark.django_db
class TestWaitlistPositionAdjustment:
    """Tests for waitlist position adjustment."""

    def test_position_adjusted_on_delete(self, create_meetup, create_meetup_user, create_waitlist):
        """Test positions are adjusted when entry is deleted."""
        meetup = create_meetup()
        user1 = create_meetup_user(name='User1', email='user1@example.com')
        user2 = create_meetup_user(name='User2', email='user2@example.com')
        user3 = create_meetup_user(name='User3', email='user3@example.com')

        waitlist1 = create_waitlist(user1, meetup, position=1)
        waitlist2 = create_waitlist(user2, meetup, position=2)
        waitlist3 = create_waitlist(user3, meetup, position=3)

        # Delete first entry
        waitlist1.delete()

        waitlist2.refresh_from_db()
        waitlist3.refresh_from_db()

        assert waitlist2.position == 1
        assert waitlist3.position == 2
