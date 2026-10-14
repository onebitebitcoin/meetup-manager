import pytest
from django.db import IntegrityError

from lite.models import LiteConfig, Meetup, Member, Rsvp


def test_member_token_and_name_unique(db):
    a = Member.objects.create(name='a')
    assert len(a.token) >= 32
    with pytest.raises(IntegrityError):
        Member.objects.create(name='a')


def test_meetup_checkin_code_is_four_digits(make_meetup):
    meetup = make_meetup()
    assert len(meetup.checkin_code) == 4 and meetup.checkin_code.isdigit()


def test_rsvp_unique(member, make_meetup):
    meetup = make_meetup()
    Rsvp.objects.create(member=member, meetup=meetup, status='going')
    with pytest.raises(IntegrityError):
        Rsvp.objects.create(member=member, meetup=meetup, status='maybe')


def test_legacy_meetup_id_unique(db):
    from django.utils import timezone
    kw = {'title': 't', 'starts_at': timezone.now(), 'location': 'l', 'capacity': 3}
    Meetup.objects.create(legacy_meetup_id=1, **kw)
    with pytest.raises(IntegrityError):
        Meetup.objects.create(legacy_meetup_id=1, **kw)


def test_config_singleton(db):
    LiteConfig.get()
    LiteConfig(vote_threshold=9).save()
    assert LiteConfig.objects.count() == 1
    assert LiteConfig.get().vote_threshold == 9


def test_auth_missing_token(api_client, db):
    r = api_client.get('/api/lite/me/')
    assert r.status_code == 401
    assert r.json() == {'error': '이름을 먼저 입력해 주세요'}


def test_auth_invalid_token(api_client, db):
    r = api_client.get('/api/lite/me/', HTTP_X_MEMBER_TOKEN='nope')
    assert r.status_code == 401
    assert r.json()['error'] == '이름을 먼저 입력해 주세요'


def test_host_only_forbidden(api_client, member, auth):
    r = api_client.post('/api/lite/meetups/', {}, format='json', **auth(member))
    assert r.status_code == 403
    assert r.json() == {'error': '운영자만 할 수 있어요'}


def test_host_only_without_token_is_401(api_client, db):
    assert api_client.post('/api/lite/meetups/', {}, format='json').status_code == 401


def test_me(api_client, member, auth):
    r = api_client.get('/api/lite/me/', **auth(member))
    assert r.status_code == 200
    assert r.json() == {'member': {'id': member.id, 'name': '민수', 'is_host': False}}
