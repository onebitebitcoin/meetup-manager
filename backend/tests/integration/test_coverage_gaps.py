"""
Integration tests targeting specific coverage gaps identified in the coverage report.
Covers: user_attended_meetups, register_user, admin edge cases, user_meetups with month,
auth email login, reviews edge cases, and registration status variants.
"""
import uuid
from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from meetups.models import Registration, Review

# ---------------------------------------------------------------------------
# user_attended_meetups
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestUserAttendedMeetupsAPI:

    def _past_kwargs(self):
        past = timezone.now() - timedelta(hours=2)
        return {'date_time': past - timedelta(hours=2), 'end_time': past}

    def test_returns_ended_meetups_registered_for(self, authenticated_client, create_meetup, create_registration):
        client, user, meetup_user = authenticated_client()
        meetup = create_meetup(**self._past_kwargs())
        create_registration(meetup_user, meetup)

        response = client.get(reverse('user-attended-meetups'))
        assert response.status_code == 200
        assert any(m['id'] == meetup.id for m in response.data['meetups'])

    def test_returns_ended_meetups_created(self, authenticated_client, create_meetup):
        client, user, meetup_user = authenticated_client()
        meetup = create_meetup(creator=meetup_user, **self._past_kwargs())

        response = client.get(reverse('user-attended-meetups'))
        assert response.status_code == 200
        assert any(m['id'] == meetup.id for m in response.data['meetups'])

    def test_excludes_future_meetups(self, authenticated_client, create_meetup, create_registration):
        client, user, meetup_user = authenticated_client()
        future = create_meetup()
        create_registration(meetup_user, future)

        response = client.get(reverse('user-attended-meetups'))
        assert not any(m['id'] == future.id for m in response.data['meetups'])

    def test_has_review_true_when_reviewed(self, authenticated_client, create_meetup, create_registration):
        client, user, meetup_user = authenticated_client()
        meetup = create_meetup(**self._past_kwargs())
        create_registration(meetup_user, meetup)
        Review.objects.create(meetup=meetup, user=meetup_user, rating=5, content='Great!')

        response = client.get(reverse('user-attended-meetups'))
        m = next(m for m in response.data['meetups'] if m['id'] == meetup.id)
        assert m['has_review'] is True

    def test_has_review_false_when_not_reviewed(self, authenticated_client, create_meetup, create_registration):
        client, user, meetup_user = authenticated_client()
        meetup = create_meetup(**self._past_kwargs())
        create_registration(meetup_user, meetup)

        response = client.get(reverse('user-attended-meetups'))
        m = next(m for m in response.data['meetups'] if m['id'] == meetup.id)
        assert m['has_review'] is False

    def test_unauthenticated_returns_401(self, api_client):
        assert api_client.get(reverse('user-attended-meetups')).status_code == 401

    def test_ended_by_date_time_no_end_time(self, authenticated_client, create_meetup, create_registration):
        client, user, meetup_user = authenticated_client()
        meetup = create_meetup(date_time=timezone.now() - timedelta(hours=1))
        create_registration(meetup_user, meetup)

        response = client.get(reverse('user-attended-meetups'))
        assert any(m['id'] == meetup.id for m in response.data['meetups'])


# ---------------------------------------------------------------------------
# user_meetups with month parameter
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestUserMeetupsWithMonthParam:

    def test_month_param_filters(self, authenticated_client, create_meetup):
        client, user, meetup_user = authenticated_client()
        url = reverse('user-meetups')
        response = client.get(url, {'month': '2025-01'})
        assert response.status_code == 200
        assert 'data' in response.data
        assert 'meta' in response.data

    def test_invalid_month_string_returns_400(self, authenticated_client):
        client, user, meetup_user = authenticated_client()
        response = client.get(reverse('user-meetups'), {'month': 'invalid'})
        assert response.status_code == 400

    def test_invalid_month_number_returns_400(self, authenticated_client):
        client, user, meetup_user = authenticated_client()
        response = client.get(reverse('user-meetups'), {'month': '2025-13'})
        assert response.status_code == 400

    def test_december_edge_case(self, authenticated_client):
        client, user, meetup_user = authenticated_client()
        response = client.get(reverse('user-meetups'), {'month': '2025-12'})
        assert response.status_code == 200

    def test_pagination_params(self, authenticated_client):
        client, user, meetup_user = authenticated_client()
        response = client.get(reverse('user-meetups'), {'page': '1', 'page_size': '5'})
        assert response.status_code == 200
        assert response.data['meta']['page_size'] == 5

    def test_invalid_pagination_defaults(self, authenticated_client):
        client, user, meetup_user = authenticated_client()
        response = client.get(reverse('user-meetups'), {'page': 'bad', 'page_size': 'bad'})
        assert response.status_code == 200


# ---------------------------------------------------------------------------
# Legacy register_user endpoint
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestLegacyRegisterUserAPI:

    def test_success(self, api_client, create_meetup_user, create_meetup):
        user = create_meetup_user(name='LegacyUser', email='legacy@example.com')
        meetup = create_meetup()
        response = api_client.post(reverse('register-user'),
                                   {'user_id': user.id, 'meetup_id': meetup.id}, format='json')
        assert response.status_code == 201
        assert Registration.objects.filter(user=user, meetup=meetup).exists()

    def test_invalid_ids(self, api_client):
        response = api_client.post(reverse('register-user'),
                                   {'user_id': 99999, 'meetup_id': 99999}, format='json')
        assert response.status_code == 400

    def test_registration_list_view(self, api_client, create_meetup_user, create_meetup, create_registration):
        u = create_meetup_user(name='ListUser', email='listuser@example.com')
        m = create_meetup()
        create_registration(u, m)
        response = api_client.get(reverse('registration-list'))
        assert response.status_code == 200


# ---------------------------------------------------------------------------
# Admin edge cases
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestAdminEdgeCases:

    def test_cannot_delete_admin_user(self, authenticated_client, create_meetup_user):
        client, user, meetup_user = authenticated_client(is_admin=True)
        target = create_meetup_user(name='AdminTarget', email='admintarget@example.com', is_admin=True)
        response = client.delete(reverse('admin-delete-user', kwargs={'user_id': target.id}))
        assert response.status_code == 400

    def test_reset_password_user_without_django_account(self, authenticated_client):
        from meetups.models import MeetupUser
        client, admin_user, _ = authenticated_client(is_admin=True)
        guest = MeetupUser.objects.create(name='GuestNoAccount', email='guestnoac@example.com')
        response = client.post(reverse('admin-reset-password', kwargs={'user_id': guest.id}),
                               {'new_password': 'newpass123'}, format='json')
        assert response.status_code == 400


# ---------------------------------------------------------------------------
# Auth edge cases
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestAuthEdgeCases:

    def test_email_login_success(self, api_client, create_user):
        create_user(username='emailloginuser', email='emaillogin@example.com', password='testpass123')
        response = api_client.post(reverse('auth-login'),
                                   {'username': 'emaillogin@example.com', 'password': 'testpass123'},
                                   format='json')
        assert response.status_code == 200

    def test_email_login_wrong_password(self, api_client, create_user):
        create_user(username='emailwrong', email='emailwrong@example.com', password='testpass123')
        response = api_client.post(reverse('auth-login'),
                                   {'username': 'emailwrong@example.com', 'password': 'wrongpass'},
                                   format='json')
        assert response.status_code == 401

    def test_change_password_unauthenticated(self, api_client):
        response = api_client.post(reverse('auth-change-password'),
                                   {'current_password': 'old', 'new_password': 'new'}, format='json')
        assert response.status_code == 401

    def test_change_password_missing_fields(self, authenticated_client):
        client, user, _ = authenticated_client()
        response = client.post(reverse('auth-change-password'), {}, format='json')
        assert response.status_code == 400

    def test_lightning_address_missing_field(self, authenticated_client):
        client, user, _ = authenticated_client()
        response = client.put(reverse('auth-lightning-address'), {}, format='json')
        assert response.status_code == 400

    def test_lightning_address_clear_with_empty_string(self, authenticated_client):
        client, user, meetup_user = authenticated_client()
        meetup_user.lightning_address = 'alice@coinos.io'
        meetup_user.save()
        response = client.put(reverse('auth-lightning-address'), {'lightning_address': ''}, format='json')
        assert response.status_code == 200
        meetup_user.refresh_from_db()
        assert meetup_user.lightning_address == ''

    def test_account_settings_unauthenticated(self, api_client):
        assert api_client.get(reverse('auth-account-settings')).status_code == 401

    def test_test_invoice_unauthenticated(self, api_client):
        response = api_client.post(reverse('auth-test-lightning-invoice'),
                                   {'lightning_address': 'alice@coinos.io'}, format='json')
        assert response.status_code == 401


# ---------------------------------------------------------------------------
# Review view edge cases
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestReviewEdgeCases:

    def _past_kwargs(self):
        past = timezone.now() - timedelta(hours=2)
        return {'date_time': past - timedelta(hours=2), 'end_time': past}

    def test_review_feed_invalid_page_defaults(self, api_client):
        response = api_client.get(reverse('review-feed'), {'page': 'bad', 'page_size': 'bad'})
        assert response.status_code == 200
        assert response.data['page'] == 1

    def test_get_review_not_eligible_no_review(self, authenticated_client, create_meetup):
        client, user, meetup_user = authenticated_client()
        meetup = create_meetup()
        url = reverse('meetup-review', kwargs={'meetup_id': meetup.id})
        response = client.get(url)
        assert response.status_code == 200
        assert response.data['review'] is None
        assert response.data['can_write'] is False

    def test_meetup_reviews_list_empty_avg_rating_zero(self, api_client, create_meetup):
        meetup = create_meetup(**self._past_kwargs())
        response = api_client.get(reverse('meetup-reviews-list', kwargs={'meetup_id': meetup.id}))
        assert response.status_code == 200
        assert response.data['average_rating'] == 0

    def test_admin_can_write_review_for_ended_meetup(self, authenticated_client, create_meetup):
        client, user, meetup_user = authenticated_client(is_admin=True)
        meetup = create_meetup(**self._past_kwargs())
        url = reverse('meetup-review', kwargs={'meetup_id': meetup.id})
        response = client.post(url, {'rating': 4, 'content': '관리자 후기'}, format='json')
        assert response.status_code == 201

    def test_delete_review(self, authenticated_client, create_meetup, create_registration):
        client, user, meetup_user = authenticated_client()
        meetup = create_meetup(**self._past_kwargs())
        create_registration(meetup_user, meetup)
        Review.objects.create(meetup=meetup, user=meetup_user, rating=3, content='delete me')
        url = reverse('meetup-review', kwargs={'meetup_id': meetup.id})
        response = client.delete(url)
        assert response.status_code == 200
        assert not Review.objects.filter(meetup=meetup, user=meetup_user).exists()

    def test_meetup_reviews_list_nonexistent_meetup(self, api_client):
        response = api_client.get(reverse('meetup-reviews-list', kwargs={'meetup_id': 99999}))
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# Registration status and meetup detail edge cases
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestMeetupViewEdgeCases:

    def test_check_status_unauthenticated_returns_false(self, api_client, create_meetup):
        meetup = create_meetup()
        response = api_client.get(reverse('check-registration-status', kwargs={'meetup_id': meetup.id}))
        assert response.status_code == 200
        assert response.data['is_registered'] is False

    def test_check_status_registered(self, authenticated_client, create_meetup, create_registration):
        client, user, meetup_user = authenticated_client()
        meetup = create_meetup()
        create_registration(meetup_user, meetup)
        response = client.get(reverse('check-registration-status', kwargs={'meetup_id': meetup.id}))
        assert response.status_code == 200
        assert response.data['is_registered'] is True

    def test_put_meetup_unauthenticated(self, api_client, create_meetup):
        meetup = create_meetup()
        response = api_client.put(reverse('meetup-detail', kwargs={'pk': meetup.id}),
                                  {'name': 'New'}, format='json')
        assert response.status_code == 401

    def test_put_meetup_non_creator_forbidden(self, authenticated_client, create_meetup):
        client, user, meetup_user = authenticated_client()
        meetup = create_meetup()
        response = client.put(reverse('meetup-detail', kwargs={'pk': meetup.id}),
                              {'name': 'New'}, format='json')
        assert response.status_code == 403

    def test_delete_meetup_as_creator(self, authenticated_client, create_meetup):
        client, user, meetup_user = authenticated_client()
        meetup = create_meetup(creator=meetup_user)
        response = client.delete(reverse('meetup-detail', kwargs={'pk': meetup.id}))
        assert response.status_code == 204

    def test_meetup_registrations_list(self, authenticated_client, create_meetup, create_registration, create_meetup_user):
        client, user, meetup_user = authenticated_client()
        meetup = create_meetup()
        p = create_meetup_user(name='RegP', email=f'regp_{uuid.uuid4().hex[:6]}@example.com')
        create_registration(p, meetup)
        response = client.get(reverse('meetup-registrations', kwargs={'meetup_id': meetup.id}))
        assert response.status_code == 200
        assert len(response.data['registrations']) >= 1
