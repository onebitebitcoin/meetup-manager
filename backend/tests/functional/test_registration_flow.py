"""
Functional tests for complete registration flow.
"""
import pytest
from django.urls import reverse

from meetups.models import Registration, Meetup


@pytest.mark.django_db
class TestRegistrationFlow:
    """End-to-end tests for registration flow."""

    def test_complete_registration_flow(self, authenticated_client, create_meetup):
        """Test complete registration flow from signup to meetup registration."""
        client, user, meetup_user = authenticated_client()

        # Create a meetup
        meetup = create_meetup(name='Test Meetup', max_participants=10)
        initial_participants = meetup.current_participants

        # Register for meetup
        register_url = reverse('register-for-meetup', kwargs={'meetup_id': meetup.id})
        response = client.post(register_url)
        assert response.status_code == 201

        # Verify registration
        meetup.refresh_from_db()
        assert meetup.current_participants == initial_participants + 1
        assert Registration.objects.filter(user=meetup_user, meetup=meetup).exists()

        # Check registration status
        status_url = reverse('check-registration-status', kwargs={'meetup_id': meetup.id})
        response = client.get(status_url)
        assert response.status_code == 200
        assert response.data['is_registered'] is True

        # Unregister from meetup
        unregister_url = reverse('unregister-from-meetup', kwargs={'meetup_id': meetup.id})
        response = client.delete(unregister_url)
        assert response.status_code == 200

        # Verify unregistration
        meetup.refresh_from_db()
        assert meetup.current_participants == initial_participants
        assert not Registration.objects.filter(user=meetup_user, meetup=meetup).exists()

    def test_registration_prevents_duplicate(self, authenticated_client, create_meetup, create_registration):
        """Test that duplicate registration is prevented."""
        client, user, meetup_user = authenticated_client()
        meetup = create_meetup(max_participants=10)

        # First registration
        create_registration(meetup_user, meetup)

        # Try to register again
        register_url = reverse('register-for-meetup', kwargs={'meetup_id': meetup.id})
        response = client.post(register_url)

        assert response.status_code == 400

    def test_registration_respects_capacity(self, authenticated_client, create_meetup, create_meetup_user, create_registration):
        """Test that registration respects max capacity."""
        client, user, meetup_user = authenticated_client()
        meetup = create_meetup(max_participants=2)

        # Fill the meetup
        user1 = create_meetup_user(name='User1', email='user1@example.com')
        user2 = create_meetup_user(name='User2', email='user2@example.com')
        create_registration(user1, meetup)
        create_registration(user2, meetup)

        # Try to register for full meetup
        register_url = reverse('register-for-meetup', kwargs={'meetup_id': meetup.id})
        response = client.post(register_url)

        assert response.status_code == 400

    def test_user_meetups_list(self, authenticated_client, create_meetup, create_registration):
        """Test getting list of user's registered meetups."""
        client, user, meetup_user = authenticated_client()

        # Register for multiple meetups
        meetup1 = create_meetup(name='Meetup 1')
        meetup2 = create_meetup(name='Meetup 2')
        create_registration(meetup_user, meetup1)
        create_registration(meetup_user, meetup2)

        # Get user's meetups
        url = reverse('user-meetups')
        response = client.get(url)

        assert response.status_code == 200
        assert len(response.data) == 2

    def test_multiple_users_registration(self, api_client, create_meetup, create_meetup_user, create_registration):
        """Test multiple users registering for same meetup."""
        meetup = create_meetup(max_participants=5)

        # Create and register multiple users
        for i in range(3):
            user = create_meetup_user(name=f'User{i}', email=f'user{i}@example.com')
            create_registration(user, meetup)

        meetup.refresh_from_db()
        assert meetup.current_participants == 3
        assert meetup.available_spots == 2
        assert meetup.is_full is False
