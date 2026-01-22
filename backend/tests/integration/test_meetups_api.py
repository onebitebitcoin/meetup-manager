"""
Integration tests for meetups API endpoints.
"""
import pytest
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from meetups.models import Meetup, Registration


@pytest.mark.django_db
class TestMeetupListAPI:
    """Tests for meetup list endpoint."""

    def test_list_meetups(self, api_client, create_meetup):
        """Test listing all meetups."""
        create_meetup(name='Meetup 1')
        create_meetup(name='Meetup 2')

        url = reverse('meetup-list-create')
        response = api_client.get(url)

        assert response.status_code == 200
        assert len(response.data) == 2

    def test_list_meetups_empty(self, api_client):
        """Test listing meetups when none exist."""
        url = reverse('meetup-list-create')
        response = api_client.get(url)

        assert response.status_code == 200
        assert len(response.data) == 0


@pytest.mark.django_db
class TestMeetupCreateAPI:
    """Tests for meetup creation endpoint."""

    def test_create_meetup_authenticated(self, authenticated_client):
        """Test creating meetup as authenticated user."""
        client, user, meetup_user = authenticated_client()

        url = reverse('meetup-list-create')
        data = {
            'name': 'New Meetup',
            'description': 'A new meetup',
            'date_time': (timezone.now() + timedelta(days=7)).isoformat(),
            'location': 'Seoul',
            'max_participants': 20,
            'creator': meetup_user.id
        }

        response = client.post(url, data, format='json')
        assert response.status_code == 201
        assert Meetup.objects.filter(name='New Meetup').exists()


@pytest.mark.django_db
class TestMeetupDetailAPI:
    """Tests for meetup detail endpoint."""

    def test_get_meetup_detail(self, api_client, create_meetup):
        """Test getting meetup detail."""
        meetup = create_meetup(name='Detail Meetup', description='Test Description')

        url = reverse('meetup-detail', kwargs={'pk': meetup.id})
        response = api_client.get(url)

        assert response.status_code == 200
        assert response.data['name'] == 'Detail Meetup'
        assert response.data['description'] == 'Test Description'

    def test_get_meetup_not_found(self, api_client):
        """Test getting non-existent meetup."""
        url = reverse('meetup-detail', kwargs={'pk': 99999})
        response = api_client.get(url)

        assert response.status_code == 404

    def test_update_meetup(self, authenticated_client, create_meetup):
        """Test updating meetup."""
        client, user, meetup_user = authenticated_client(is_admin=True)
        meetup = create_meetup(name='Original Name', creator=meetup_user)

        url = reverse('meetup-detail', kwargs={'pk': meetup.id})
        data = {'name': 'Updated Name'}

        response = client.put(url, data, format='json')
        assert response.status_code == 200

        meetup.refresh_from_db()
        assert meetup.name == 'Updated Name'

    def test_delete_meetup(self, authenticated_client, create_meetup):
        """Test deleting meetup."""
        client, user, meetup_user = authenticated_client(is_admin=True)
        meetup = create_meetup(name='To Delete', creator=meetup_user)

        url = reverse('meetup-detail', kwargs={'pk': meetup.id})
        response = client.delete(url)

        assert response.status_code in [200, 204]
        assert not Meetup.objects.filter(id=meetup.id).exists()


@pytest.mark.django_db
class TestMeetupRegistrationAPI:
    """Tests for meetup registration endpoints."""

    def test_register_for_meetup(self, authenticated_client, create_meetup):
        """Test registering for a meetup."""
        client, user, meetup_user = authenticated_client()
        meetup = create_meetup(max_participants=10)

        url = reverse('register-for-meetup', kwargs={'meetup_id': meetup.id})
        response = client.post(url)

        assert response.status_code == 201
        assert Registration.objects.filter(user=meetup_user, meetup=meetup).exists()

    def test_register_for_full_meetup(self, authenticated_client, create_meetup):
        """Test registering for a full meetup fails."""
        client, user, meetup_user = authenticated_client()
        meetup = create_meetup(max_participants=1)
        meetup.current_participants = 1
        meetup.save()

        url = reverse('register-for-meetup', kwargs={'meetup_id': meetup.id})
        response = client.post(url)

        assert response.status_code == 400

    def test_unregister_from_meetup(self, authenticated_client, create_meetup, create_registration):
        """Test unregistering from a meetup."""
        client, user, meetup_user = authenticated_client()
        meetup = create_meetup(max_participants=10)
        create_registration(meetup_user, meetup)

        url = reverse('unregister-from-meetup', kwargs={'meetup_id': meetup.id})
        response = client.delete(url)

        assert response.status_code == 200
        assert not Registration.objects.filter(user=meetup_user, meetup=meetup).exists()

    def test_check_registration_status(self, authenticated_client, create_meetup, create_registration):
        """Test checking registration status."""
        client, user, meetup_user = authenticated_client()
        meetup = create_meetup()
        create_registration(meetup_user, meetup)

        url = reverse('check-registration-status', kwargs={'meetup_id': meetup.id})
        response = client.get(url)

        assert response.status_code == 200
        assert response.data['is_registered'] is True

    def test_get_meetup_registrations(self, api_client, create_meetup, create_meetup_user, create_registration):
        """Test getting list of meetup registrations."""
        meetup = create_meetup()
        user1 = create_meetup_user(name='User 1', email='user1@example.com')
        user2 = create_meetup_user(name='User 2', email='user2@example.com')
        create_registration(user1, meetup)
        create_registration(user2, meetup)

        url = reverse('meetup-registrations', kwargs={'meetup_id': meetup.id})
        response = api_client.get(url)

        assert response.status_code == 200
        assert len(response.data) == 2
