"""
Integration tests for authentication API endpoints.
"""
import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from meetups.models import MeetupUser


@pytest.mark.django_db
class TestAuthRegisterAPI:
    """Tests for user registration endpoint."""

    def test_register_success(self, api_client):
        """Test successful user registration."""
        url = reverse('auth-register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'securepass123'
        }

        response = api_client.post(url, data, format='json')

        assert response.status_code == 201
        assert User.objects.filter(username='newuser').exists()
        assert MeetupUser.objects.filter(email='newuser@example.com').exists()

    def test_register_duplicate_username(self, api_client, create_user):
        """Test registration fails with duplicate username."""
        create_user(username='existinguser', email='existing@example.com')

        url = reverse('auth-register')
        data = {
            'username': 'existinguser',
            'email': 'new@example.com',
            'password': 'securepass123'
        }

        response = api_client.post(url, data, format='json')
        assert response.status_code == 400

    def test_register_invalid_username(self, api_client):
        """Test registration fails with invalid username."""
        url = reverse('auth-register')
        data = {
            'username': 'ab',  # Too short
            'email': 'user@example.com',
            'password': 'securepass123'
        }

        response = api_client.post(url, data, format='json')
        assert response.status_code == 400


@pytest.mark.django_db
class TestAuthLoginAPI:
    """Tests for user login endpoint."""

    def test_login_success(self, api_client, create_user):
        """Test successful login."""
        create_user(username='testuser', email='test@example.com', password='testpass123')

        url = reverse('auth-login')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }

        response = api_client.post(url, data, format='json')
        assert response.status_code == 200
        assert 'user' in response.data

    def test_login_wrong_password(self, api_client, create_user):
        """Test login fails with wrong password."""
        create_user(username='testuser', email='test@example.com', password='testpass123')

        url = reverse('auth-login')
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }

        response = api_client.post(url, data, format='json')
        assert response.status_code == 401

    def test_login_nonexistent_user(self, api_client):
        """Test login fails with nonexistent user."""
        url = reverse('auth-login')
        data = {
            'username': 'nonexistent',
            'password': 'password123'
        }

        response = api_client.post(url, data, format='json')
        assert response.status_code == 401


@pytest.mark.django_db
class TestAuthLogoutAPI:
    """Tests for user logout endpoint."""

    def test_logout_success(self, authenticated_client):
        """Test successful logout."""
        client, user, meetup_user = authenticated_client()

        url = reverse('auth-logout')
        response = client.post(url)

        assert response.status_code == 200


@pytest.mark.django_db
class TestUsernameCheckAPI:
    """Tests for username availability check endpoint."""

    def test_username_available(self, api_client):
        """Test username is available."""
        url = reverse('check-username')
        response = api_client.get(url, {'username': 'newuser'})

        assert response.status_code == 200
        assert response.data['available'] is True

    def test_username_taken(self, api_client, create_user):
        """Test username is taken."""
        create_user(username='existinguser', email='existing@example.com')

        url = reverse('check-username')
        response = api_client.get(url, {'username': 'existinguser'})

        assert response.status_code == 200
        assert response.data['available'] is False
