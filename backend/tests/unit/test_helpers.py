"""
Unit tests for meetups/views/helpers.py utility functions.
"""
import pytest
from rest_framework.test import APIRequestFactory


@pytest.mark.django_db
class TestParseDatetimeIso:

    def test_valid_iso_with_timezone(self):
        from meetups.views.helpers import parse_datetime_iso
        dt, err = parse_datetime_iso('2025-06-01T10:00:00+09:00')
        assert err is None
        assert dt is not None

    def test_valid_iso_with_z_suffix(self):
        from meetups.views.helpers import parse_datetime_iso
        dt, err = parse_datetime_iso('2025-06-01T10:00:00Z')
        assert err is None
        assert dt is not None

    def test_valid_naive_datetime_made_aware(self):
        from meetups.views.helpers import parse_datetime_iso
        dt, err = parse_datetime_iso('2025-06-01T10:00:00')
        assert err is None
        assert dt is not None
        assert dt.tzinfo is not None

    def test_empty_string_returns_error(self):
        from meetups.views.helpers import parse_datetime_iso
        dt, err = parse_datetime_iso('')
        assert dt is None
        assert err is not None
        assert err.status_code == 400

    def test_none_returns_error(self):
        from meetups.views.helpers import parse_datetime_iso
        dt, err = parse_datetime_iso(None)
        assert dt is None
        assert err is not None

    def test_invalid_format_returns_error(self):
        from meetups.views.helpers import parse_datetime_iso
        dt, err = parse_datetime_iso('not-a-date')
        assert dt is None
        assert err is not None
        assert err.status_code == 400


@pytest.mark.django_db
class TestEnsureAuthenticated:

    def test_authenticated_returns_none(self, create_user):
        from meetups.views.helpers import ensure_authenticated
        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = create_user()
        assert ensure_authenticated(request) is None

    def test_unauthenticated_returns_401(self):
        from django.contrib.auth.models import AnonymousUser

        from meetups.views.helpers import ensure_authenticated
        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = AnonymousUser()
        response = ensure_authenticated(request)
        assert response is not None
        assert response.status_code == 401

    def test_custom_error_body(self):
        from django.contrib.auth.models import AnonymousUser

        from meetups.views.helpers import ensure_authenticated
        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = AnonymousUser()
        response = ensure_authenticated(request, error_body={'error': 'custom'})
        assert response.data == {'error': 'custom'}


@pytest.mark.django_db
class TestGetMeetupOrResponse:

    def test_existing_meetup_returned(self, create_meetup):
        from meetups.views.helpers import get_meetup_or_response
        meetup = create_meetup()
        result, err = get_meetup_or_response(meetup.id)
        assert err is None
        assert result.id == meetup.id

    def test_nonexistent_meetup_returns_404(self):
        from meetups.views.helpers import get_meetup_or_response
        result, err = get_meetup_or_response(99999)
        assert result is None
        assert err is not None
        assert err.status_code == 404

    def test_custom_lookup_field(self, create_meetup):
        from meetups.views.helpers import get_meetup_or_response
        meetup = create_meetup(name='LookupByName')
        result, err = get_meetup_or_response('LookupByName', lookup_field='name')
        assert err is None
        assert result.id == meetup.id


@pytest.mark.django_db
class TestEnsureMeetupCreatorOrAdmin:

    def test_creator_returns_none(self, create_meetup, create_meetup_user):
        from meetups.views.helpers import ensure_meetup_creator_or_admin
        creator = create_meetup_user(name='Creator', email='creator_h@example.com')
        meetup = create_meetup(creator=creator)
        assert ensure_meetup_creator_or_admin(meetup, creator) is None

    def test_admin_returns_none(self, create_meetup, create_meetup_user):
        from meetups.views.helpers import ensure_meetup_creator_or_admin
        admin = create_meetup_user(name='Admin', email='admin_h@example.com', is_admin=True)
        meetup = create_meetup()
        assert ensure_meetup_creator_or_admin(meetup, admin) is None

    def test_non_creator_non_admin_returns_403(self, create_meetup, create_meetup_user):
        from meetups.views.helpers import ensure_meetup_creator_or_admin
        other = create_meetup_user(name='Other', email='other_h@example.com')
        meetup = create_meetup()
        result = ensure_meetup_creator_or_admin(meetup, other)
        assert result is not None
        assert result.status_code == 403


@pytest.mark.django_db
class TestEnsureMeetupCreator:

    def test_creator_returns_none(self, create_meetup, create_meetup_user):
        from meetups.views.helpers import ensure_meetup_creator
        creator = create_meetup_user(name='Creator2', email='creator2_h@example.com')
        meetup = create_meetup(creator=creator)
        assert ensure_meetup_creator(meetup, creator) is None

    def test_non_creator_returns_403(self, create_meetup, create_meetup_user):
        from meetups.views.helpers import ensure_meetup_creator
        other = create_meetup_user(name='NotCreator', email='notcreator_h@example.com')
        meetup = create_meetup()
        result = ensure_meetup_creator(meetup, other)
        assert result is not None
        assert result.status_code == 403
