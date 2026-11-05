import pytest
from django.contrib.auth.hashers import check_password
from django.core.cache import cache

from lite.models import DEFAULT_ADMIN_PASSWORD_HASH, LiteConfig

LOGIN = '/api/lite/admin/login/'
PASSWORD = '/api/lite/admin/password/'
SETTINGS = '/api/lite/admin/settings/'
INITIAL = 'hanip'


def login(client, headers, password):
    return client.post(LOGIN, {'password': password}, format='json', **headers)


def change(client, headers, current, new):
    return client.put(PASSWORD, {'current_password': current, 'new_password': new}, format='json', **headers)


def test_기본_해시는_초기_비밀번호와_맞고_기존_행에도_들어간다(db):
    assert check_password(INITIAL, DEFAULT_ADMIN_PASSWORD_HASH)
    assert LiteConfig.get().admin_password_hash == DEFAULT_ADMIN_PASSWORD_HASH


def test_올바른_비밀번호면_운영자가_된다(api_client, member, auth):
    r = login(api_client, auth(member), INITIAL)
    assert r.status_code == 200 and r.json()['member']['is_host'] is True
    member.refresh_from_db()
    assert member.is_host


def test_틀린_비밀번호는_403(api_client, member, auth):
    r = login(api_client, auth(member), 'wrong')
    assert r.status_code == 403 and r.json() == {'error': '비밀번호가 맞지 않아요'}
    member.refresh_from_db()
    assert not member.is_host


def test_비밀번호_형식이_틀려도_403(api_client, member, auth):
    r = api_client.post(LOGIN, {'password': 123}, format='json', **auth(member))
    assert r.status_code == 403


def test_토큰이_없으면_401(api_client):
    assert login(api_client, {}, INITIAL).status_code == 401


@pytest.mark.closed
def test_오픈_전에도_로그인할_수_있다(api_client, member, auth):
    assert login(api_client, auth(member), INITIAL).status_code == 200


def test_로그인은_다섯_번_넘으면_429(api_client, member, auth):
    cache.clear()
    for _ in range(5):
        assert login(api_client, auth(member), 'wrong').status_code == 403
    assert login(api_client, auth(member), INITIAL).status_code == 429


def test_비밀번호_변경_성공_후_이전_비밀번호는_거부된다(api_client, member, host, auth):
    r = change(api_client, auth(host), INITIAL, 'new-password-1')
    assert r.status_code == 200 and r.json() == {'changed': True}
    assert login(api_client, auth(member), INITIAL).status_code == 403
    assert login(api_client, auth(member), 'new-password-1').status_code == 200
    assert 'new-password-1' not in LiteConfig.get().admin_password_hash


def test_현재_비밀번호가_틀리면_403(api_client, host, auth):
    r = change(api_client, auth(host), 'wrong', 'new-password-1')
    assert r.status_code == 403
    assert check_password(INITIAL, LiteConfig.get().admin_password_hash)


@pytest.mark.parametrize('new', ['short', '1234567', None, 12345678])
def test_새_비밀번호가_8자_미만이면_400(api_client, host, auth, new):
    r = change(api_client, auth(host), INITIAL, new)
    assert r.status_code == 400
    assert check_password(INITIAL, LiteConfig.get().admin_password_hash)


def test_비밀번호_변경은_운영자만(api_client, member, auth):
    assert change(api_client, auth(member), INITIAL, 'new-password-1').status_code == 403
    assert change(api_client, {}, INITIAL, 'new-password-1').status_code == 401


def test_비밀번호_변경도_다섯_번_넘으면_429(api_client, host, auth):
    for _ in range(5):
        assert change(api_client, auth(host), 'wrong', 'new-password-1').status_code == 403
    assert change(api_client, auth(host), INITIAL, 'new-password-1').status_code == 429


def test_SPA_경로는_admin과_admin_슬래시_모두_Vue로_간다(api_client, settings, tmp_path):
    (tmp_path / 'frontend_dist').mkdir()
    (tmp_path / 'frontend_dist' / 'index.html').write_text('<html>spa</html>')
    settings.BASE_DIR = tmp_path
    for path in ('/admin', '/admin/', '/admin/settings', '/admin/login/'):
        r = api_client.get(path)
        assert r.status_code == 200, path
        assert b'spa' in b''.join(r.streaming_content), path


# ---- 설정 ----

def test_설정_조회는_해시를_포함하지_않는다(api_client, host, auth):
    r = api_client.get(SETTINGS, **auth(host))
    assert r.status_code == 200
    body = r.json()
    assert set(body) == {'vote_threshold', 'seminar_guide_1', 'seminar_guide_2', 'seminar_guide_3', 'seminar_guide_4', 'join_guide'}
    assert 'pbkdf2' not in r.content.decode()
    assert body['vote_threshold'] == 5


def test_설정_수정은_보낸_필드만_바꾸고_같은_형식으로_응답한다(api_client, host, auth):
    before = api_client.get(SETTINGS, **auth(host)).json()
    r = api_client.patch(SETTINGS, {'vote_threshold': 3, 'join_guide': '환영해요'}, format='json', **auth(host))
    assert r.status_code == 200
    body = r.json()
    assert body['vote_threshold'] == 3 and body['join_guide'] == '환영해요'
    assert body['seminar_guide_1'] == before['seminar_guide_1']
    assert 'pbkdf2' not in r.content.decode()
    config = LiteConfig.get()
    assert config.vote_threshold == 3 and config.join_guide == '환영해요'


def test_설정은_운영자만_쓸_수_있다(api_client, member, auth):
    assert api_client.get(SETTINGS, **auth(member)).status_code == 403
    assert api_client.patch(SETTINGS, {'vote_threshold': 3}, format='json', **auth(member)).status_code == 403
    assert LiteConfig.get().vote_threshold == 5


def test_설정은_토큰이_없으면_401(api_client):
    assert api_client.get(SETTINGS).status_code == 401
    assert api_client.patch(SETTINGS, {'vote_threshold': 3}, format='json').status_code == 401


@pytest.mark.parametrize('payload', [
    {'vote_threshold': 0}, {'vote_threshold': -1}, {'vote_threshold': '3'}, {'vote_threshold': True},
    {'vote_threshold': 1.5}, {'join_guide': '   '}, {'join_guide': ''}, {'seminar_guide_2': 5},
    {'seminar_guide_3': 'a' * 1001},
])
def test_잘못된_값은_400이고_아무것도_바꾸지_않는다(api_client, host, auth, payload):
    r = api_client.patch(SETTINGS, {**payload, 'seminar_guide_1': '바꾸면 안 돼요'}, format='json', **auth(host))
    assert r.status_code == 400 and r.json()['error']
    config = LiteConfig.get()
    assert config.vote_threshold == 5 and config.seminar_guide_1 != '바꾸면 안 돼요'


@pytest.mark.parametrize('field', ['is_open', 'admin_password_hash', 'id', 'unknown'])
def test_허용되지_않은_필드는_400(api_client, host, auth, field):
    before = LiteConfig.get().admin_password_hash
    r = api_client.patch(SETTINGS, {field: 'x', 'vote_threshold': 3}, format='json', **auth(host))
    assert r.status_code == 400 and field in r.json()['error']
    config = LiteConfig.get()
    assert config.admin_password_hash == before and config.vote_threshold == 5 and config.is_open is True
