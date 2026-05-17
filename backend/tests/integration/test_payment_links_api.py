"""
Integration tests for payment link API endpoints.
"""
import uuid
from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from meetups.models import MeetupPaymentLink


@pytest.mark.django_db
class TestCreatePaymentLinkAPI:

    def test_create_payment_link_success(self, authenticated_client, create_meetup, monkeypatch):
        client, user, meetup_user = authenticated_client(is_admin=True)
        meetup_user.lightning_address = 'alice@coinos.io'
        meetup_user.save()
        meetup = create_meetup(creator=meetup_user)

        def fake_invoice(_address):
            return {
                'lnurlp_url': 'https://coinos.io/.well-known/lnurlp/alice',
                'callback_url': 'https://coinos.io/lnurl/callback?amount=1000',
                'invoice': 'lnbc10n1p0fakeinvoice',
            }

        monkeypatch.setattr('meetups.views.payment_links.create_one_sat_invoice', fake_invoice)

        url = reverse('create-payment-link', kwargs={'meetup_id': meetup.id})
        response = client.post(url)
        assert response.status_code == 201
        assert 'token' in response.data
        assert 'bolt11' in response.data
        assert MeetupPaymentLink.objects.filter(meetup=meetup).exists()

    def test_create_link_without_lightning_address_fails(self, authenticated_client, create_meetup):
        client, user, meetup_user = authenticated_client(is_admin=True)
        meetup_user.lightning_address = ''
        meetup_user.save()
        meetup = create_meetup(creator=meetup_user)

        url = reverse('create-payment-link', kwargs={'meetup_id': meetup.id})
        response = client.post(url)
        assert response.status_code == 400

    def test_non_creator_cannot_create_link(self, authenticated_client, create_meetup):
        client, user, meetup_user = authenticated_client(is_admin=False)
        meetup = create_meetup()  # different creator

        url = reverse('create-payment-link', kwargs={'meetup_id': meetup.id})
        response = client.post(url)
        assert response.status_code in [403, 404]

    def test_unauthenticated_cannot_create_link(self, api_client, create_meetup):
        meetup = create_meetup()
        url = reverse('create-payment-link', kwargs={'meetup_id': meetup.id})
        response = api_client.post(url)
        assert response.status_code == 401


@pytest.mark.django_db
class TestGetPaymentLinkAPI:

    def _create_link(self, create_meetup, create_meetup_user, bolt11, expires_delta):
        creator = create_meetup_user(name='PLCreator', email=f'pl_{uuid.uuid4().hex[:6]}@example.com')
        meetup = create_meetup(creator=creator)
        return MeetupPaymentLink.objects.create(
            meetup=meetup,
            bolt11=bolt11,
            expires_at=timezone.now() + expires_delta,
        )

    def test_get_valid_link_returns_bolt11(self, api_client, create_meetup, create_meetup_user):
        link = self._create_link(create_meetup, create_meetup_user, 'lnbc10n1p0valid', timedelta(hours=1))
        url = reverse('get-payment-link', kwargs={'token': str(link.token)})
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.data['bolt11'] == 'lnbc10n1p0valid'
        assert response.data['is_expired'] is False

    def test_get_valid_link_includes_meetup_name(self, api_client, create_meetup, create_meetup_user):
        creator = create_meetup_user(name='NameCreator', email='namedpl@example.com')
        meetup = create_meetup(name='Bitcoin 모임', creator=creator)
        link = MeetupPaymentLink.objects.create(
            meetup=meetup,
            bolt11='lnbc10n1p0named',
            expires_at=timezone.now() + timedelta(hours=1),
        )
        url = reverse('get-payment-link', kwargs={'token': str(link.token)})
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.data['meetup_name'] == 'Bitcoin 모임'

    def test_get_expired_link_shows_expired_flag(self, api_client, create_meetup, create_meetup_user):
        link = self._create_link(create_meetup, create_meetup_user, 'lnbc10n1p0expired', -timedelta(hours=1))
        url = reverse('get-payment-link', kwargs={'token': str(link.token)})
        response = api_client.get(url)
        if response.status_code == 200:
            assert response.data['is_expired'] is True
        else:
            assert response.status_code in [400, 410]

    def test_get_nonexistent_link_returns_404(self, api_client):
        url = reverse('get-payment-link', kwargs={'token': str(uuid.uuid4())})
        response = api_client.get(url)
        assert response.status_code == 404

    def test_get_link_is_public_no_auth_required(self, api_client, create_meetup, create_meetup_user):
        link = self._create_link(create_meetup, create_meetup_user, 'lnbc10n1p0public', timedelta(hours=1))
        url = reverse('get-payment-link', kwargs={'token': str(link.token)})
        response = api_client.get(url)
        assert response.status_code == 200
