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


def rename(client, headers, name):
    return client.patch('/api/lite/me/', {'name': name}, format='json', **headers)


def test_이름만_바꾸고_토큰과_기록은_그대로다(api_client, member, auth):
    token = member.token
    r = rename(api_client, auth(member), '느긋한 수달')
    assert r.status_code == 200 and r.json()['member']['name'] == '느긋한 수달'
    member.refresh_from_db()
    assert member.name == '느긋한 수달' and member.token == token


def test_이름_바꾸기_검증(api_client, member, make_member, auth):
    make_member('바쁜 다람쥐')
    assert rename(api_client, auth(member), '바쁜 다람쥐').status_code == 409
    assert rename(api_client, auth(member), '운영자').status_code == 400
    assert rename(api_client, auth(member), '').status_code == 400
    assert rename(api_client, {}, '새 이름').status_code in (401, 403)


def test_이름_바꾸기는_횟수를_제한하고_내_정보_조회는_세지_않는다(api_client, member, auth):
    for i in range(20):
        assert rename(api_client, auth(member), f'이름{i}').status_code == 200
    assert rename(api_client, auth(member), '이름끝').status_code == 429
    assert api_client.get('/api/lite/me/', **auth(member)).status_code == 200
