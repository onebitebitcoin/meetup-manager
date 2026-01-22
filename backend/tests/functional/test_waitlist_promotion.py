"""
Functional tests for waitlist promotion flow.
"""
import pytest
from django.urls import reverse

from meetups.models import Notification, Registration, Waitlist


@pytest.mark.django_db
class TestWaitlistPromotionFlow:
    """End-to-end tests for waitlist promotion flow."""

    def test_waitlist_auto_promotion_on_unregister(self, create_meetup, create_meetup_user, create_registration, create_waitlist):
        """Test that waitlisted user is promoted when spot opens."""
        meetup = create_meetup(max_participants=2)

        # Fill the meetup
        user1 = create_meetup_user(name='User1', email='user1@example.com')
        user2 = create_meetup_user(name='User2', email='user2@example.com')
        reg1 = create_registration(user1, meetup)
        create_registration(user2, meetup)

        # Add user to waitlist
        waitlist_user = create_meetup_user(name='Waitlist User', email='waitlist@example.com')
        create_waitlist(waitlist_user, meetup, position=1)

        assert meetup.is_full

        # User1 unregisters
        reg1.delete()

        # Verify waitlist user was promoted
        meetup.refresh_from_db()
        assert Registration.objects.filter(user=waitlist_user, meetup=meetup).exists()
        assert not Waitlist.objects.filter(user=waitlist_user, meetup=meetup).exists()

    def test_waitlist_promotion_respects_order(self, create_meetup, create_meetup_user, create_registration, create_waitlist):
        """Test that waitlist promotion respects position order."""
        meetup = create_meetup(max_participants=1)

        # Fill the meetup
        user1 = create_meetup_user(name='User1', email='user1@example.com')
        reg1 = create_registration(user1, meetup)

        # Add multiple users to waitlist
        waitlist_user1 = create_meetup_user(name='Waitlist1', email='waitlist1@example.com')
        waitlist_user2 = create_meetup_user(name='Waitlist2', email='waitlist2@example.com')
        create_waitlist(waitlist_user1, meetup, position=1)
        create_waitlist(waitlist_user2, meetup, position=2)

        # User1 unregisters
        reg1.delete()

        # Verify first waitlist user was promoted (not second)
        assert Registration.objects.filter(user=waitlist_user1, meetup=meetup).exists()
        assert not Registration.objects.filter(user=waitlist_user2, meetup=meetup).exists()
        assert Waitlist.objects.filter(user=waitlist_user2, meetup=meetup).exists()

    def test_waitlist_notification_on_promotion(self, create_meetup, create_meetup_user, create_registration, create_waitlist):
        """Test that notification is created on waitlist promotion."""
        meetup = create_meetup(max_participants=1)

        # Fill the meetup
        user1 = create_meetup_user(name='User1', email='user1@example.com')
        reg1 = create_registration(user1, meetup)

        # Add user to waitlist
        waitlist_user = create_meetup_user(name='Waitlist User', email='waitlist@example.com')
        create_waitlist(waitlist_user, meetup, position=1)

        # Delete registration to trigger promotion
        reg1.delete()

        # Check for notification
        notifications = Notification.objects.filter(
            user=waitlist_user,
            meetup=meetup,
            notification_type='waitlist_promotion'
        )
        assert notifications.exists()

    def test_complete_waitlist_flow(self, authenticated_client, create_meetup, create_meetup_user, create_registration, create_waitlist):
        """Test complete waitlist flow from joining to promotion."""
        client, user, meetup_user = authenticated_client()
        meetup = create_meetup(max_participants=1)

        # Fill the meetup
        other_user = create_meetup_user(name='Other', email='other@example.com')
        reg = create_registration(other_user, meetup)

        # Join waitlist
        join_url = reverse('add-to-waitlist', kwargs={'meetup_id': meetup.id})
        response = client.post(join_url)
        assert response.status_code == 201

        # Verify on waitlist
        status_url = reverse('check-waitlist-status', kwargs={'meetup_id': meetup.id})
        response = client.get(status_url)
        assert response.data['is_waitlisted'] is True

        # Other user unregisters
        reg.delete()

        # Verify promoted to registration
        reg_status_url = reverse('check-registration-status', kwargs={'meetup_id': meetup.id})
        response = client.get(reg_status_url)
        assert response.data['is_registered'] is True

        # Verify removed from waitlist
        response = client.get(status_url)
        assert response.data['is_waitlisted'] is False

    def test_waitlist_position_updates_after_promotion(self, create_meetup, create_meetup_user, create_registration, create_waitlist):
        """Test that waitlist positions update after promotion."""
        meetup = create_meetup(max_participants=1)

        # Fill the meetup
        user1 = create_meetup_user(name='User1', email='user1@example.com')
        reg1 = create_registration(user1, meetup)

        # Add multiple users to waitlist
        waitlist_user1 = create_meetup_user(name='Waitlist1', email='waitlist1@example.com')
        waitlist_user2 = create_meetup_user(name='Waitlist2', email='waitlist2@example.com')
        waitlist_user3 = create_meetup_user(name='Waitlist3', email='waitlist3@example.com')

        create_waitlist(waitlist_user1, meetup, position=1)
        wl2 = create_waitlist(waitlist_user2, meetup, position=2)
        wl3 = create_waitlist(waitlist_user3, meetup, position=3)

        # Promote first user
        reg1.delete()

        # Check remaining positions
        wl2.refresh_from_db()
        wl3.refresh_from_db()

        assert wl2.position == 1
        assert wl3.position == 2
