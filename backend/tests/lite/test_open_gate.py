import pytest
from django.utils import timezone

from lite.models import LiteConfig, Meetup

pytestmark = pytest.mark.closed

NOT_OPEN = {'error': '아직 오픈 전이에요'}


@pytest.fixture
def meetup(db):
    return Meetup.objects.create(title='모임', starts_at=timezone.now() + timezone.timedelta(days=1), location='l', capacity=5)


def test_closed_by_default_and_home_reports_it(api_client, member, auth):
    assert LiteConfig.get().is_open is False
    assert api_client.get('/api/lite/home/').json()['is_open'] is False


def test_closed_blocks_participation_for_members(api_client, member, meetup, auth):
    h = auth(member)
    room_id = meetup.room.id
    checks = [
        api_client.put(f'/api/lite/meetups/{meetup.id}/rsvp/', {'status': 'going'}, format='json', **h),
        api_client.get(f'/api/lite/rooms/{room_id}/messages/', **h),
        api_client.post(f'/api/lite/rooms/{room_id}/messages/', {'body': 'hi'}, format='json', **h),
        api_client.post('/api/lite/seminar/', **h),
        api_client.get('/api/lite/requests/', **h),
        api_client.post('/api/lite/requests/', {'title': 't', 'preferred_period': 'any'}, format='json', **h),
    ]
    for r in checks:
        assert r.status_code == 403 and r.json() == NOT_OPEN


def test_closed_still_allows_browsing_signup_and_host_claim(api_client, meetup, settings):
    settings.LITE_HOST_KEY = 'k'
    assert api_client.get('/api/lite/home/').status_code == 200
    assert api_client.get(f'/api/lite/meetups/{meetup.id}/').status_code == 200
    r = api_client.post('/api/lite/members/', {'name': '새사람'}, format='json')
    assert r.status_code == 201
    token = r.json()['token']
    r = api_client.post('/api/lite/host/claim/', {'key': 'k'}, format='json', HTTP_X_MEMBER_TOKEN=token)
    assert r.status_code == 200 and r.json()['member']['is_host'] is True


def test_host_uses_everything_while_closed(api_client, host, meetup, auth):
    h = auth(host)
    assert api_client.get(f'/api/lite/rooms/{meetup.room.id}/messages/', **h).status_code == 200
    assert api_client.post(f'/api/lite/rooms/{meetup.room.id}/messages/', {'body': 'hi'}, format='json', **h).status_code == 201


def test_host_toggles_open(api_client, host, member, meetup, auth):
    assert api_client.put('/api/lite/admin/open/', {'is_open': True}, format='json', **auth(member)).status_code == 403
    assert api_client.put('/api/lite/admin/open/', {'is_open': 'yes'}, format='json', **auth(host)).status_code == 400

    r = api_client.put('/api/lite/admin/open/', {'is_open': True}, format='json', **auth(host))
    assert r.status_code == 200 and r.json() == {'is_open': True}
    r = api_client.put(f'/api/lite/meetups/{meetup.id}/rsvp/', {'status': 'going'}, format='json', **auth(member))
    assert r.status_code == 200

    api_client.put('/api/lite/admin/open/', {'is_open': False}, format='json', **auth(host))
    assert api_client.get(f'/api/lite/rooms/{meetup.room.id}/messages/', **auth(member)).status_code == 403
