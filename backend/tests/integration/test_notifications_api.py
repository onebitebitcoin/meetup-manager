"""
Integration tests for notifications API endpoints.
"""
import pytest
from django.urls import reverse

from meetups.models import Notification


@pytest.mark.django_db
class TestGetNotificationsAPI:

    def test_get_empty_notifications(self, authenticated_client):
        client, user, meetup_user = authenticated_client()
        url = reverse('user-notifications')
        response = client.get(url)
        assert response.status_code == 200
        assert response.data['notifications'] == []
        assert response.data['unread_count'] == 0

    def test_get_notifications_returns_own_only(self, authenticated_client, create_notification, create_meetup_user):
        client, user, meetup_user = authenticated_client()
        other = create_meetup_user(name='Other', email='other_notif@example.com')
        create_notification(meetup_user, title='Mine')
        create_notification(other, title='Not Mine')

        url = reverse('user-notifications')
        response = client.get(url)
        assert response.status_code == 200
        notifs = response.data['notifications']
        assert len(notifs) == 1
        assert notifs[0]['title'] == 'Mine'

    def test_get_notifications_unauthenticated(self, api_client):
        url = reverse('user-notifications')
        response = api_client.get(url)
        assert response.status_code == 401

    def test_notification_time_ago_field_present(self, authenticated_client, create_notification):
        client, user, meetup_user = authenticated_client()
        create_notification(meetup_user, title='Recent')
        url = reverse('user-notifications')
        response = client.get(url)
        assert '전' in response.data['notifications'][0]['time_ago']

    def test_unread_notification_defaults_to_false(self, authenticated_client, create_notification):
        client, user, meetup_user = authenticated_client()
        create_notification(meetup_user, title='Unread')
        url = reverse('user-notifications')
        response = client.get(url)
        assert response.data['notifications'][0]['is_read'] is False


@pytest.mark.django_db
class TestMarkNotificationReadAPI:

    def test_mark_single_notification_read(self, authenticated_client, create_notification):
        client, user, meetup_user = authenticated_client()
        notif = create_notification(meetup_user, title='Mark Me')

        url = reverse('mark-notification-read', kwargs={'notification_id': notif.id})
        response = client.post(url)
        assert response.status_code == 200

        notif.refresh_from_db()
        assert notif.is_read is True

    def test_cannot_mark_other_users_notification(self, authenticated_client, create_notification, create_meetup_user):
        client, user, meetup_user = authenticated_client()
        other = create_meetup_user(name='Other2', email='other2_notif@example.com')
        notif = create_notification(other, title="Not Mine")

        url = reverse('mark-notification-read', kwargs={'notification_id': notif.id})
        response = client.post(url)
        assert response.status_code in [403, 404]

        notif.refresh_from_db()
        assert notif.is_read is False

    def test_mark_all_notifications_read(self, authenticated_client, create_notification):
        client, user, meetup_user = authenticated_client()
        notif1 = create_notification(meetup_user, title='N1')
        notif2 = create_notification(meetup_user, title='N2')
        notif3 = create_notification(meetup_user, title='N3')

        url = reverse('mark-all-notifications-read')
        response = client.post(url)
        assert response.status_code == 200

        for n in [notif1, notif2, notif3]:
            n.refresh_from_db()
            assert n.is_read is True

    def test_mark_all_read_does_not_affect_other_users(self, authenticated_client, create_notification, create_meetup_user):
        client, user, meetup_user = authenticated_client()
        other = create_meetup_user(name='Other3', email='other3_notif@example.com')
        other_notif = create_notification(other, title='Others')
        create_notification(meetup_user, title='Mine')

        url = reverse('mark-all-notifications-read')
        client.post(url)

        other_notif.refresh_from_db()
        assert other_notif.is_read is False


@pytest.mark.django_db
class TestDeleteNotificationAPI:

    def test_delete_own_notification(self, authenticated_client, create_notification):
        client, user, meetup_user = authenticated_client()
        notif = create_notification(meetup_user, title='Delete Me')

        url = reverse('delete-notification', kwargs={'notification_id': notif.id})
        response = client.delete(url)
        assert response.status_code == 200
        assert not Notification.objects.filter(id=notif.id).exists()

    def test_cannot_delete_other_users_notification(self, authenticated_client, create_notification, create_meetup_user):
        client, user, meetup_user = authenticated_client()
        other = create_meetup_user(name='Other4', email='other4_notif@example.com')
        notif = create_notification(other, title='Not Mine')

        url = reverse('delete-notification', kwargs={'notification_id': notif.id})
        response = client.delete(url)
        assert response.status_code in [403, 404]
        assert Notification.objects.filter(id=notif.id).exists()

    def test_delete_nonexistent_notification(self, authenticated_client):
        client, user, meetup_user = authenticated_client()
        url = reverse('delete-notification', kwargs={'notification_id': 99999})
        response = client.delete(url)
        assert response.status_code == 404


@pytest.mark.django_db
class TestSendNotificationAPI:

    def test_admin_can_send_to_all_participants(
        self, authenticated_client, create_meetup, create_registration, create_meetup_user
    ):
        client, user, meetup_user = authenticated_client(is_admin=True)
        meetup = create_meetup(creator=meetup_user)
        p1 = create_meetup_user(name='P1', email='p1_notif@example.com')
        p2 = create_meetup_user(name='P2', email='p2_notif@example.com')
        create_registration(p1, meetup)
        create_registration(p2, meetup)

        url = reverse('send-notification-to-participants', kwargs={'meetup_id': meetup.id})
        response = client.post(url, {'title': '공지', 'message': '내일 뵙겠습니다'}, format='json')
        assert response.status_code == 200
        assert Notification.objects.filter(user=p1, meetup=meetup).exists()
        assert Notification.objects.filter(user=p2, meetup=meetup).exists()

    def test_send_notification_missing_title_fails(self, authenticated_client, create_meetup):
        client, user, meetup_user = authenticated_client(is_admin=True)
        meetup = create_meetup(creator=meetup_user)

        url = reverse('send-notification-to-participants', kwargs={'meetup_id': meetup.id})
        response = client.post(url, {'message': '메시지만'}, format='json')
        assert response.status_code == 400

    def test_non_admin_cannot_send_notification(self, authenticated_client, create_meetup):
        client, user, meetup_user = authenticated_client(is_admin=False)
        meetup = create_meetup()

        url = reverse('send-notification-to-participants', kwargs={'meetup_id': meetup.id})
        response = client.post(url, {'title': '공지', 'message': '메시지'}, format='json')
        assert response.status_code in [403, 404]
