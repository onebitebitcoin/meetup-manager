from datetime import timedelta

from django.utils import timezone

from lite.models import Meetup


def make_meetup():
    return Meetup.objects.create(title='보드게임', starts_at=timezone.now() + timedelta(days=2), location='홍대', capacity=8)


def test_home_without_name_lists_meetups(api_client, db):
    meetup = make_meetup()
    r = api_client.get('/api/lite/home/')
    assert r.status_code == 200
    body = r.json()
    assert [m['id'] for m in body['meetups']] == [meetup.id]
    assert body['meetups'][0]['my_status'] is None
    assert body['my_seminar'] is None and body['seminars'] == []


def test_meetup_detail_without_name(api_client, db):
    meetup = make_meetup()
    r = api_client.get(f'/api/lite/meetups/{meetup.id}/')
    assert r.status_code == 200
    body = r.json()
    assert body['meetup']['title'] == '보드게임'
    assert body['removed'] is False and 'checkin_code' not in body


def test_rsvp_still_needs_name(api_client, db):
    meetup = make_meetup()
    r = api_client.put(f'/api/lite/meetups/{meetup.id}/rsvp/', {'status': 'going'}, format='json')
    assert r.status_code == 401
    assert r.json() == {'error': '이름을 먼저 입력해 주세요'}


def test_invalid_token_is_still_rejected_on_public_view(api_client, db):
    r = api_client.get('/api/lite/home/', HTTP_X_MEMBER_TOKEN='nope')
    assert r.status_code == 401
