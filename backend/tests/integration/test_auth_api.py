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
        assert response.status_code == 404


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


@pytest.mark.django_db
class TestLightningAddressAPI:
    """Tests for lightning address endpoints."""

    def test_get_lightning_address_success(self, authenticated_client):
        client, _, _ = authenticated_client()

        url = reverse('auth-lightning-address')
        response = client.get(url)

        assert response.status_code == 200
        assert response.data['lightning_address'] == ''

    def test_set_lightning_address_success(self, authenticated_client):
        client, _, meetup_user = authenticated_client()

        url = reverse('auth-lightning-address')
        response = client.put(url, {'lightning_address': 'alice@coinos.io'}, format='json')

        meetup_user.refresh_from_db()
        assert response.status_code == 200
        assert response.data['lightning_address'] == 'alice@coinos.io'
        assert meetup_user.lightning_address == 'alice@coinos.io'

    def test_set_lightning_address_invalid(self, authenticated_client):
        client, _, _ = authenticated_client()

        url = reverse('auth-lightning-address')
        response = client.put(url, {'lightning_address': 'invalid-address'}, format='json')

        assert response.status_code == 400
        assert 'error' in response.data

    def test_test_invoice_success(self, authenticated_client, monkeypatch):
        client, _, _ = authenticated_client()

        responses = [
            {
                'tag': 'payRequest',
                'callback': 'https://coinos.io/lnurl/callback',
                'minSendable': 1000,
                'maxSendable': 100000000,
            },
            {
                'pr': 'lnbc10n1p0testinvoice',
            },
        ]

        def fake_fetch_json_with_timeout(_url):
            return responses.pop(0)

        monkeypatch.setattr('meetups.views.auth.fetch_json_with_timeout', fake_fetch_json_with_timeout)

        url = reverse('auth-test-lightning-invoice')
        response = client.post(url, {'lightning_address': 'alice@coinos.io'}, format='json')

        assert response.status_code == 200
        assert response.data['invoice']['amount_sats'] == 1
        assert response.data['invoice']['bolt11'] == 'lnbc10n1p0testinvoice'

    def test_test_invoice_amount_not_supported(self, authenticated_client, monkeypatch):
        client, _, _ = authenticated_client()

        def fake_fetch_json_with_timeout(_url):
            return {
                'tag': 'payRequest',
                'callback': 'https://coinos.io/lnurl/callback',
                'minSendable': 2000,
                'maxSendable': 100000000,
            }

        monkeypatch.setattr('meetups.views.auth.fetch_json_with_timeout', fake_fetch_json_with_timeout)

        url = reverse('auth-test-lightning-invoice')
        response = client.post(url, {'lightning_address': 'alice@coinos.io'}, format='json')

        assert response.status_code == 400
        assert '1 sats 인보이스를 지원하지 않습니다' in response.data['error']
