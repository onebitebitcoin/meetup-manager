import pytest

from lite.models import Member


def test_create_member(api_client, db):
    r = api_client.post('/api/lite/members/', {'name': '  철수  '}, format='json')
    assert r.status_code == 201
    body = r.json()
    assert body['member']['name'] == '철수'
    assert body['member']['is_host'] is False
    assert Member.objects.get(name='철수').token == body['token']


@pytest.mark.parametrize('name', ['', '   ', 'a' * 21, None, 5])
def test_create_member_invalid(api_client, db, name):
    r = api_client.post('/api/lite/members/', {'name': name}, format='json')
    assert r.status_code == 400
    assert r.json()['error']


def test_create_member_duplicate(api_client, member):
    r = api_client.post('/api/lite/members/', {'name': '민수'}, format='json')
    assert r.status_code == 409


def test_create_member_throttled(api_client, db):
    for i in range(60):
        assert api_client.post('/api/lite/members/', {'name': f'u{i}'}, format='json').status_code == 201
    r = api_client.post('/api/lite/members/', {'name': 'extra'}, format='json')
    assert r.status_code == 429
    assert r.json() == {'error': '잠시 후 다시 시도해 주세요'}


def test_host_claim_success(api_client, member, auth, settings):
    settings.LITE_HOST_KEY = 'secret'
    r = api_client.post('/api/lite/host/claim/', {'key': 'secret'}, format='json', **auth(member))
    assert r.status_code == 200 and r.json()['member']['is_host'] is True
    member.refresh_from_db()
    assert member.is_host


def test_host_claim_wrong_key(api_client, member, auth, settings):
    settings.LITE_HOST_KEY = 'secret'
    r = api_client.post('/api/lite/host/claim/', {'key': 'bad'}, format='json', **auth(member))
    assert r.status_code == 403


def test_host_claim_disabled_when_key_empty(api_client, member, auth, settings):
    settings.LITE_HOST_KEY = ''
    r = api_client.post('/api/lite/host/claim/', {'key': ''}, format='json', **auth(member))
    assert r.status_code == 403
