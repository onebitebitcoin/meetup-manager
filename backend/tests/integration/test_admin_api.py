"""
Integration tests for admin API endpoints.
"""
import pytest
from django.urls import reverse

from meetups.models import Meetup, MeetupUser, Registration


@pytest.mark.django_db
class TestAdminUsersListAPI:

    def test_admin_can_list_users(self, authenticated_client, create_meetup_user):
        client, user, meetup_user = authenticated_client(is_admin=True)
        create_meetup_user(name='UserA', email='usera_adm@example.com')
        url = reverse('admin-users-list')
        response = client.get(url)
        assert response.status_code == 200
        assert isinstance(response.data, list)

    def test_non_admin_cannot_list_users(self, authenticated_client):
        client, user, meetup_user = authenticated_client(is_admin=False)
        url = reverse('admin-users-list')
        response = client.get(url)
        assert response.status_code == 403

    def test_unauthenticated_cannot_list_users(self, api_client):
        url = reverse('admin-users-list')
        response = api_client.get(url)
        assert response.status_code == 401

    def test_user_list_includes_registration_count(
        self, authenticated_client, create_meetup_user, create_meetup, create_registration
    ):
        client, user, meetup_user = authenticated_client(is_admin=True)
        target = create_meetup_user(name='Active', email='active_adm@example.com')
        meetup = create_meetup()
        create_registration(target, meetup)

        url = reverse('admin-users-list')
        response = client.get(url)
        target_data = next((u for u in response.data if u['email'] == 'active_adm@example.com'), None)
        assert target_data is not None
        assert target_data.get('registered_meetups_count', 0) >= 1


@pytest.mark.django_db
class TestAdminDeleteUserAPI:

    def test_admin_can_delete_user(self, authenticated_client, create_meetup_user):
        client, user, meetup_user = authenticated_client(is_admin=True)
        target = create_meetup_user(name='ToDelete', email='todelete_adm@example.com')

        url = reverse('admin-delete-user', kwargs={'user_id': target.id})
        response = client.delete(url)
        assert response.status_code == 200
        assert not MeetupUser.objects.filter(id=target.id).exists()

    def test_non_admin_cannot_delete_user(self, authenticated_client, create_meetup_user):
        client, user, meetup_user = authenticated_client(is_admin=False)
        target = create_meetup_user(name='Safe', email='safe_adm@example.com')

        url = reverse('admin-delete-user', kwargs={'user_id': target.id})
        response = client.delete(url)
        assert response.status_code == 403
        assert MeetupUser.objects.filter(id=target.id).exists()

    def test_delete_nonexistent_user_returns_404(self, authenticated_client):
        client, user, meetup_user = authenticated_client(is_admin=True)
        url = reverse('admin-delete-user', kwargs={'user_id': 99999})
        response = client.delete(url)
        assert response.status_code == 404


@pytest.mark.django_db
class TestAdminToggleAdminAPI:

    def test_toggle_admin_on(self, authenticated_client, create_meetup_user):
        client, user, meetup_user = authenticated_client(is_admin=True)
        target = create_meetup_user(name='ToToggle', email='totoggle_adm@example.com')
        assert target.is_admin is False

        url = reverse('admin-toggle-user-admin', kwargs={'user_id': target.id})
        response = client.post(url)
        assert response.status_code == 200
        target.refresh_from_db()
        assert target.is_admin is True

    def test_toggle_admin_off(self, authenticated_client, create_meetup_user):
        client, user, meetup_user = authenticated_client(is_admin=True)
        target = create_meetup_user(name='AlreadyAdmin', email='alreadyadmin_adm@example.com', is_admin=True)

        url = reverse('admin-toggle-user-admin', kwargs={'user_id': target.id})
        client.post(url)
        target.refresh_from_db()
        assert target.is_admin is False

    def test_non_admin_cannot_toggle(self, authenticated_client, create_meetup_user):
        client, user, meetup_user = authenticated_client(is_admin=False)
        target = create_meetup_user(name='NoToggle', email='notoggle_adm@example.com')

        url = reverse('admin-toggle-user-admin', kwargs={'user_id': target.id})
        response = client.post(url)
        assert response.status_code == 403


@pytest.mark.django_db
class TestAdminStatisticsAPI:

    def test_admin_gets_statistics(self, authenticated_client):
        client, user, meetup_user = authenticated_client(is_admin=True)
        url = reverse('admin-statistics')
        response = client.get(url)
        assert response.status_code == 200
        assert any(k in response.data for k in ('total_users', 'users', 'total_meetups', 'meetups'))

    def test_non_admin_cannot_get_statistics(self, authenticated_client):
        client, user, meetup_user = authenticated_client(is_admin=False)
        url = reverse('admin-statistics')
        response = client.get(url)
        assert response.status_code == 403


@pytest.mark.django_db
class TestAdminResetPasswordAPI:

    def test_admin_resets_user_password(self, authenticated_client, create_user):
        client, admin_user, admin_meetup = authenticated_client(is_admin=True)
        target_django = create_user(username='resetme_adm', email='resetme_adm@example.com', password='oldpass')
        target_meetup = MeetupUser.objects.create(
            user=target_django, name='resetme_adm', email='resetme_adm@example.com'
        )

        url = reverse('admin-reset-password', kwargs={'user_id': target_meetup.id})
        response = client.post(url, {'new_password': 'newSecure123'}, format='json')
        assert response.status_code == 200
        target_django.refresh_from_db()
        assert target_django.check_password('newSecure123')

    def test_non_admin_cannot_reset_password(self, authenticated_client, create_meetup_user):
        client, user, meetup_user = authenticated_client(is_admin=False)
        target = create_meetup_user(name='ResetTarget', email='resettarget_adm@example.com')

        url = reverse('admin-reset-password', kwargs={'user_id': target.id})
        response = client.post(url, {'new_password': 'newpass'}, format='json')
        assert response.status_code == 403


@pytest.mark.django_db
class TestAdminMeetupsListAPI:

    def test_admin_lists_meetups(self, authenticated_client, create_meetup):
        client, user, meetup_user = authenticated_client(is_admin=True)
        create_meetup(name='Admin View Meetup')
        url = reverse('admin-meetups-list')
        response = client.get(url)
        assert response.status_code == 200
        assert isinstance(response.data, list)

    def test_non_admin_cannot_list_meetups(self, authenticated_client):
        client, user, meetup_user = authenticated_client(is_admin=False)
        url = reverse('admin-meetups-list')
        response = client.get(url)
        assert response.status_code == 403

    def test_admin_deletes_meetup(self, authenticated_client, create_meetup):
        client, user, meetup_user = authenticated_client(is_admin=True)
        meetup = create_meetup(name='Delete Me')
        url = reverse('admin-delete-meetup', kwargs={'meetup_id': meetup.id})
        response = client.delete(url)
        assert response.status_code == 200
        assert not Meetup.objects.filter(id=meetup.id).exists()

    def test_non_admin_cannot_delete_meetup(self, authenticated_client, create_meetup):
        client, user, meetup_user = authenticated_client(is_admin=False)
        meetup = create_meetup(name='Safe Meetup')
        url = reverse('admin-delete-meetup', kwargs={'meetup_id': meetup.id})
        response = client.delete(url)
        assert response.status_code == 403
        assert Meetup.objects.filter(id=meetup.id).exists()


@pytest.mark.django_db
class TestParticipantManagementAPI:

    def test_add_participant_by_email(self, authenticated_client, create_meetup, create_meetup_user):
        client, user, meetup_user = authenticated_client(is_admin=True)
        meetup = create_meetup(creator=meetup_user)
        participant = create_meetup_user(name='NewParticipant', email='newpart_adm@example.com')

        url = reverse('add-participant-by-email', kwargs={'meetup_id': meetup.id})
        response = client.post(url, {'email': participant.email}, format='json')
        assert response.status_code in [200, 201]
        assert Registration.objects.filter(user=participant, meetup=meetup).exists()

    def test_add_participant_nonexistent_email_returns_404(self, authenticated_client, create_meetup):
        client, user, meetup_user = authenticated_client(is_admin=True)
        meetup = create_meetup(creator=meetup_user)

        url = reverse('add-participant-by-email', kwargs={'meetup_id': meetup.id})
        response = client.post(url, {'email': 'nobody@example.com'}, format='json')
        assert response.status_code == 404

    def test_add_already_registered_participant_fails(
        self, authenticated_client, create_meetup, create_meetup_user, create_registration
    ):
        client, user, meetup_user = authenticated_client(is_admin=True)
        meetup = create_meetup(creator=meetup_user)
        participant = create_meetup_user(name='Already', email='already_adm@example.com')
        create_registration(participant, meetup)

        url = reverse('add-participant-by-email', kwargs={'meetup_id': meetup.id})
        response = client.post(url, {'email': participant.email}, format='json')
        assert response.status_code == 400

    def test_remove_participant(self, authenticated_client, create_meetup, create_meetup_user, create_registration):
        client, user, meetup_user = authenticated_client(is_admin=True)
        meetup = create_meetup(creator=meetup_user)
        participant = create_meetup_user(name='Removable', email='removable_adm@example.com')
        registration = create_registration(participant, meetup)

        url = reverse('remove-participant', kwargs={'meetup_id': meetup.id, 'registration_id': registration.id})
        response = client.delete(url)
        assert response.status_code == 200
        assert not Registration.objects.filter(id=registration.id).exists()

    def test_non_admin_cannot_remove_participant(
        self, authenticated_client, create_meetup, create_meetup_user, create_registration
    ):
        client, user, meetup_user = authenticated_client(is_admin=False)
        meetup = create_meetup()
        participant = create_meetup_user(name='Protected', email='protected_adm@example.com')
        registration = create_registration(participant, meetup)

        url = reverse('remove-participant', kwargs={'meetup_id': meetup.id, 'registration_id': registration.id})
        response = client.delete(url)
        assert response.status_code in [403, 404]
        assert Registration.objects.filter(id=registration.id).exists()
