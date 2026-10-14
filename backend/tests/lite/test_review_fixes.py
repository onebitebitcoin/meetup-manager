"""코드 리뷰 반영 사항: 횟수 제한, 채팅방 보장, 입력 검증, 쿼리 수."""
from datetime import timedelta

import pytest
from django.utils import timezone

from lite.models import ChatMessage, ChatRoom, LiteConfig, Meetup, MeetupRequest, RequestVote, SeminarRequest

THROTTLED = {'error': '잠시 후 다시 시도해 주세요'}


def post(client, url, data=None, headers=None):
    return client.post(url, data or {}, format='json', **(headers or {}))


def payload(**over):
    data = {
        'title': '보드게임', 'starts_at': (timezone.now() + timedelta(days=2)).isoformat(),
        'location': '홍대', 'capacity': 8,
    }
    data.update(over)
    return data


# --- 횟수 제한 ---

def test_member_create_throttle_is_per_ip(api_client, db):
    for i in range(60):
        assert post(api_client, '/api/lite/members/', {'name': f'u{i}'}, {'REMOTE_ADDR': '1.1.1.1'}).status_code == 201
    r = post(api_client, '/api/lite/members/', {'name': 'x'}, {'REMOTE_ADDR': '1.1.1.1'})
    assert r.status_code == 429 and r.json() == THROTTLED
    assert post(api_client, '/api/lite/members/', {'name': 'x'}, {'REMOTE_ADDR': '2.2.2.2'}).status_code == 201


def test_num_proxies_ignores_spoofed_forwarded_for(api_client, db, settings):
    from rest_framework.settings import api_settings
    settings.REST_FRAMEWORK = {**settings.REST_FRAMEWORK, 'NUM_PROXIES': 1}
    api_settings.reload()
    try:
        for i in range(60):
            h = {'HTTP_X_FORWARDED_FOR': f'9.9.9.{i}, 5.5.5.5'}
            assert post(api_client, '/api/lite/members/', {'name': f'u{i}'}, h).status_code == 201
        h = {'HTTP_X_FORWARDED_FOR': '9.9.9.200, 5.5.5.5'}
        assert post(api_client, '/api/lite/members/', {'name': 'x'}, h).status_code == 429
    finally:
        settings.REST_FRAMEWORK = {k: v for k, v in settings.REST_FRAMEWORK.items() if k != 'NUM_PROXIES'}
        api_settings.reload()


def test_host_claim_throttle(api_client, member, auth, settings):
    settings.LITE_HOST_KEY = 'secret'
    for _ in range(5):
        assert post(api_client, '/api/lite/host/claim/', {'key': 'bad'}, auth(member)).status_code == 403
    r = post(api_client, '/api/lite/host/claim/', {'key': 'secret'}, auth(member))
    assert r.status_code == 429 and r.json() == THROTTLED


def test_checkin_throttle_counts_failures_and_success(api_client, member, auth, make_meetup):
    meetup = make_meetup(days=0)
    meetup.starts_at = timezone.now() + timedelta(minutes=1)
    meetup.save()
    api_client.put(f'/api/lite/meetups/{meetup.id}/rsvp/', {'status': 'going'}, format='json', **auth(member))
    url = f'/api/lite/meetups/{meetup.id}/checkin/'
    for _ in range(4):
        assert post(api_client, url, {'code': 'x'}, auth(member)).status_code == 400
    assert post(api_client, url, {'code': meetup.checkin_code}, auth(member)).status_code in (200, 400)
    r = post(api_client, url, {'code': meetup.checkin_code}, auth(member))
    assert r.status_code == 429 and r.json() == THROTTLED


def test_checkin_throttle_is_per_meetup(api_client, member, auth, make_meetup):
    a, b = make_meetup('a'), make_meetup('b')
    for _ in range(5):
        post(api_client, f'/api/lite/meetups/{a.id}/checkin/', {'code': 'x'}, auth(member))
    assert post(api_client, f'/api/lite/meetups/{a.id}/checkin/', {'code': 'x'}, auth(member)).status_code == 429
    assert post(api_client, f'/api/lite/meetups/{b.id}/checkin/', {'code': 'x'}, auth(member)).status_code != 429


def test_message_send_throttle_only_counts_post(api_client, host, auth, make_meetup):
    room_id = make_meetup().room.id
    url = f'/api/lite/rooms/{room_id}/messages/'
    for _ in range(40):
        assert api_client.get(url, **auth(host)).status_code == 200
    for _ in range(30):
        assert post(api_client, url, {'body': 'hi'}, auth(host)).status_code == 201
    r = post(api_client, url, {'body': 'hi'}, auth(host))
    assert r.status_code == 429 and r.json() == THROTTLED
    assert api_client.get(url, **auth(host)).status_code == 200


def test_request_create_throttle(api_client, member, auth):
    for i in range(10):
        r = post(api_client, '/api/lite/requests/', {'title': f't{i}', 'preferred_period': 'any'}, auth(member))
        assert r.status_code == 201
    r = post(api_client, '/api/lite/requests/', {'title': 'x', 'preferred_period': 'any'}, auth(member))
    assert r.status_code == 429 and r.json() == THROTTLED
    assert api_client.get('/api/lite/requests/', **auth(member)).status_code == 200


def test_seminar_mode_throttle(api_client, member, auth):
    post(api_client, '/api/lite/seminar/', headers=auth(member))
    for _ in range(10):
        post(api_client, '/api/lite/seminar/mode/', {'mode': 'bad'}, auth(member))
    r = post(api_client, '/api/lite/seminar/mode/', {'mode': 'online'}, auth(member))
    assert r.status_code == 429 and r.json() == THROTTLED


# --- 채팅방 보장 ---

def test_meetup_and_seminar_rooms_created_by_model(member):
    meetup = Meetup.objects.create(title='t', starts_at=timezone.now(), location='l', capacity=2)
    assert ChatRoom.objects.get(meetup=meetup).kind == 'meetup'
    seminar = SeminarRequest.objects.create(member=member)
    assert ChatRoom.objects.get(seminar=seminar).kind == 'seminar'
    meetup.save()
    assert ChatRoom.objects.filter(meetup=meetup).count() == 1


def test_serializer_survives_missing_room(api_client, member, auth, make_meetup):
    meetup = make_meetup()
    ChatRoom.objects.filter(meetup=meetup).delete()
    r = api_client.get('/api/lite/home/', **auth(member))
    assert r.status_code == 200 and r.json()['meetups'][0]['room_id'] is None


def test_chatroom_admin_blocks_add_and_change_but_allows_cascade_delete(rf, admin_user):
    from django.contrib import admin
    model_admin = admin.site._registry[ChatRoom]
    request = rf.get('/')
    request.user = admin_user
    assert not model_admin.has_add_permission(request)
    assert not model_admin.has_change_permission(request)
    assert model_admin.has_delete_permission(request)


def test_meetup_admin_delete_is_not_blocked_by_chatroom(rf, admin_user, make_meetup):
    from django.contrib import admin
    from django.contrib.admin.utils import get_deleted_objects
    meetup = make_meetup()
    request = rf.get('/')
    request.user = admin_user
    _, _, perms_needed, _ = get_deleted_objects([meetup], request, admin.site)
    assert not perms_needed


# --- 모임 생성/rsvp 검증 ---

@pytest.mark.parametrize('starts_at', [
    '2026-13-45T10:00:00', '0001-01-01T00:00:00', '9999-12-31T23:59:59+14:00', '1999-12-31T23:59:59',
    (timezone.now() - timedelta(hours=1)).isoformat(),
])
def test_create_meetup_bad_starts_at(api_client, host, auth, starts_at):
    r = post(api_client, '/api/lite/meetups/', payload(starts_at=starts_at), auth(host))
    assert r.status_code == 400 and r.json()['error']


def test_create_meetup_description_limit(api_client, host, auth):
    assert post(api_client, '/api/lite/meetups/', payload(description='a' * 1001), auth(host)).status_code == 400
    assert post(api_client, '/api/lite/meetups/', payload(description='a' * 1000), auth(host)).status_code == 201


def test_rsvp_on_ended_meetup(api_client, member, auth, make_meetup):
    ended = make_meetup('끝', days=0)
    ended.starts_at = timezone.now() - timedelta(hours=13)
    ended.save()
    r = api_client.put(f'/api/lite/meetups/{ended.id}/rsvp/', {'status': 'going'}, format='json', **auth(member))
    assert r.status_code == 400 and r.json() == {'error': '이미 끝난 모임이에요'}
    ongoing = make_meetup('진행', days=0)
    ongoing.starts_at = timezone.now() - timedelta(hours=11)
    ongoing.save()
    r = api_client.put(f'/api/lite/meetups/{ongoing.id}/rsvp/', {'status': 'going'}, format='json', **auth(member))
    assert r.status_code == 200


# --- 메시지 조회 ---

@pytest.mark.parametrize('after', ['-1', 'x', '1.5', '9223372036854775808', '１２', '1_0'])
def test_messages_after_invalid(api_client, host, auth, make_meetup, after):
    room_id = make_meetup().room.id
    r = api_client.get(f'/api/lite/rooms/{room_id}/messages/?after={after}', **auth(host))
    assert r.status_code == 400


def test_messages_after_bounds_ok(api_client, host, auth, make_meetup):
    room_id = make_meetup().room.id
    for after in ('0', '9223372036854775807'):
        assert api_client.get(f'/api/lite/rooms/{room_id}/messages/?after={after}', **auth(host)).status_code == 200


# --- 이름 검증 ---

@pytest.mark.parametrize('name', [
    'a\nb', 'a\tb', 'a​b', '‮a', 'a\x00b', '운영자', '관리자', 'Admin', 'HOST', 'ａｄｍｉｎ', '운 영 자',
    'a b',
])
def test_create_member_rejects_bad_names(api_client, db, name):
    r = post(api_client, '/api/lite/members/', {'name': name})
    assert r.status_code == 400 and r.json()['error']


def test_create_member_nfkc_normalizes(api_client, db):
    r = post(api_client, '/api/lite/members/', {'name': 'Ａlice'})
    assert r.status_code == 201 and r.json()['member']['name'] == 'Alice'


# --- 쿼리 수 ---

def test_polling_query_count(api_client, member, auth, make_meetup, django_assert_max_num_queries):
    meetup = make_meetup()
    api_client.put(f'/api/lite/meetups/{meetup.id}/rsvp/', {'status': 'going'}, format='json', **auth(member))
    url = f'/api/lite/rooms/{meetup.room.id}/messages/?after=0'
    with django_assert_max_num_queries(3):  # 인증 + 방/권한 + 메시지
        assert api_client.get(url, **auth(member)).status_code == 200


def test_requests_list_query_count(api_client, member, make_member, auth, django_assert_max_num_queries):
    LiteConfig.get()  # 최초 생성 쿼리를 측정에서 제외
    other = make_member('철수')
    for i in range(5):
        req = MeetupRequest.objects.create(title=f'r{i}', created_by=other)
        RequestVote.objects.create(request=req, member=member)
    with django_assert_max_num_queries(4):  # 인증 + 설정 + 요청 + 내 투표
        r = api_client.get('/api/lite/requests/', **auth(member))
    assert r.status_code == 200 and all(c['voted'] for c in r.json()['requests'])


def test_host_home_query_count(api_client, host, make_member, auth, make_meetup, django_assert_max_num_queries):
    LiteConfig.get()
    make_meetup()
    for i in range(5):
        m = make_member(f'u{i}')
        seminar = SeminarRequest.objects.create(member=m)
        ChatMessage.objects.create(room=seminar.room, kind='guide', body=f'm{i}')
    with django_assert_max_num_queries(8):
        r = api_client.get('/api/lite/home/', **auth(host))
    seminars = r.json()['seminars']
    assert len(seminars) == 5 and all(s['last_message'] for s in seminars)
