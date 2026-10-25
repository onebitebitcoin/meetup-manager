from datetime import timedelta

from django.db import IntegrityError, connection
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from lite.models import ChatMessage, ChatRoom, Meetup, MeetupRequest, Rsvp

BASE = '/api/lite/admin/meetups/'


def put_rsvp(client, headers, meetup, status):
    return client.put(f'/api/lite/meetups/{meetup.id}/rsvp/', {'status': status}, format='json', **headers)


def messages(meetup):
    return list(ChatMessage.objects.filter(room=meetup.room).values_list('body', flat=True))


def patch(client, headers, meetup, **data):
    return client.patch(f'{BASE}{meetup.id}/', data, format='json', **headers)


def test_admin_apis_require_host(api_client, member, host, auth, make_meetup):
    meetup = make_meetup()
    room_id = meetup.room.id
    msg = ChatMessage.objects.create(room=meetup.room, member=member, body='hi')
    calls = [
        ('get', BASE, None),
        ('get', f'{BASE}{meetup.id}/', None),
        ('patch', f'{BASE}{meetup.id}/', {'title': 'x'}),
        ('delete', f'{BASE}{meetup.id}/', None),
        ('post', f'{BASE}{meetup.id}/cancel/', {'cancelled': True}),
        ('delete', f'{BASE}{meetup.id}/members/{member.id}/', None),
        ('delete', f'/api/lite/rooms/{room_id}/messages/{msg.id}/', None),
        ('put', f'/api/lite/rooms/{room_id}/pin/', {'message_id': msg.id}),
    ]
    for method, url, body in calls:
        r = getattr(api_client, method)(url, body, format='json', **auth(member))
        assert r.status_code == 403, (method, url)
        r = getattr(api_client, method)(url, body, format='json')
        assert r.status_code == 401, (method, url)
    assert Meetup.objects.filter(pk=meetup.pk).exists() and host


def test_list_scope(api_client, host, auth, make_meetup):
    late = make_meetup('나중', days=3)
    soon = make_meetup('먼저', days=1)
    old = make_meetup('어제', days=-2)
    older = make_meetup('그제', days=-5)
    soon.cancelled_at = timezone.now()
    soon.save()
    r = api_client.get(BASE, **auth(host))
    assert [m['id'] for m in r.json()['meetups']] == [soon.id, late.id]
    assert r.json()['meetups'][0]['cancelled'] is True
    r = api_client.get(BASE + '?scope=past', **auth(host))
    assert [m['id'] for m in r.json()['meetups']] == [old.id, older.id]
    assert api_client.get(BASE + '?scope=bogus', **auth(host)).status_code == 400


def test_detail_attendees_order(api_client, host, make_member, auth, make_meetup):
    meetup = make_meetup()
    a, b, c = make_member('가'), make_member('나'), make_member('다')
    put_rsvp(api_client, auth(a), meetup, 'no')
    put_rsvp(api_client, auth(b), meetup, 'maybe')
    put_rsvp(api_client, auth(c), meetup, 'going')
    r = api_client.get(f'{BASE}{meetup.id}/', **auth(host))
    body = r.json()
    assert [x['status'] for x in body['attendees']] == ['going', 'maybe', 'no']
    assert body['attendees'][0]['member'] == {'id': c.id, 'name': '다'}
    assert body['checkin_code'] == meetup.checkin_code
    assert body['attendees'][0]['removed'] is False and body['attendees'][0]['checked_in_at'] is None


def test_patch_success_and_schedule_message(api_client, host, auth, make_meetup):
    meetup = make_meetup()
    new_start = (timezone.now() + timedelta(days=5)).replace(hour=10, minute=0, second=0, microsecond=0)
    r = patch(api_client, auth(host), meetup, title='새 제목', starts_at=new_start.isoformat(),
              location='홍대', capacity=5, description='설명', image_url='/media/a.png')
    assert r.status_code == 200
    body = r.json()
    assert body['meetup']['title'] == '새 제목' and body['meetup']['capacity'] == 5
    assert body['description'] == '설명' and body['image_url'] == '/media/a.png'
    msgs = messages(meetup)
    assert len(msgs) == 1 and msgs[0].startswith('일정이 바뀌었어요 · ') and msgs[0].endswith(' · 홍대')
    assert '(' in msgs[0] and ':' in msgs[0]


def test_patch_without_schedule_change_has_no_message(api_client, host, auth, make_meetup):
    meetup = make_meetup()
    r = patch(api_client, auth(host), meetup, title='제목만', location=meetup.location,
              starts_at=meetup.starts_at.isoformat())
    assert r.status_code == 200
    assert messages(meetup) == []


def test_patch_allows_past_start(api_client, host, auth, make_meetup):
    meetup = make_meetup()
    past = (timezone.now() - timedelta(days=3)).isoformat()
    assert patch(api_client, auth(host), meetup, starts_at=past).status_code == 200


def test_patch_capacity_below_going(api_client, host, make_member, auth, make_meetup):
    meetup = make_meetup()
    for name in ('가', '나', '다'):
        put_rsvp(api_client, auth(make_member(name)), meetup, 'going')
    r = patch(api_client, auth(host), meetup, capacity=2)
    assert r.status_code == 400
    assert r.json()['error'] == '정원은 현재 참석 인원(3명)보다 작게 줄일 수 없어요'
    assert patch(api_client, auth(host), meetup, capacity=3).status_code == 200


def test_patch_image_url_validation(api_client, host, auth, make_meetup):
    meetup = make_meetup(image_url='/media/old.png')
    for bad in ['ftp://x.com/a.png', 'javascript:alert(1)', 'a.png', 'https://x.com/' + 'a' * 500, 5]:
        assert patch(api_client, auth(host), meetup, image_url=bad).status_code == 400, bad
    for good in ['https://x.com/a.png', 'http://x.com/a.png', '/media/b.png']:
        assert patch(api_client, auth(host), meetup, image_url=good).status_code == 200, good
    r = patch(api_client, auth(host), meetup, image_url='')
    assert r.status_code == 200 and r.json()['image_url'] == ''


def test_patch_validation_errors(api_client, host, auth, make_meetup):
    meetup = make_meetup()
    for over in [{'title': ''}, {'location': ''}, {'capacity': 1}, {'starts_at': 'bad'}, {'description': 'x' * 1001}]:
        assert patch(api_client, auth(host), meetup, **over).status_code == 400, over


def test_cancel_and_reopen(api_client, host, member, auth, make_meetup):
    meetup = make_meetup()
    url = f'{BASE}{meetup.id}/cancel/'
    r = api_client.post(url, {'cancelled': True}, format='json', **auth(host))
    assert r.status_code == 200 and r.json()['meetup']['cancelled'] is True
    meetup.refresh_from_db()
    assert meetup.cancelled_at is not None
    api_client.post(url, {'cancelled': True}, format='json', **auth(host))
    assert messages(meetup) == ['모임이 취소됐어요']
    assert put_rsvp(api_client, auth(member), meetup, 'going').status_code == 400
    r = api_client.post(url, {'cancelled': False}, format='json', **auth(host))
    assert r.json()['meetup']['cancelled'] is False
    assert messages(meetup) == ['모임이 취소됐어요', '모임이 다시 열렸어요']
    assert put_rsvp(api_client, auth(member), meetup, 'going').status_code == 200
    assert api_client.post(url, {'cancelled': 'yes'}, format='json', **auth(host)).status_code == 400


def test_cancelled_blocks_rsvp_and_checkin(api_client, host, member, auth, make_meetup):
    meetup = make_meetup(days=0)
    meetup.starts_at = timezone.now()
    meetup.save()
    assert put_rsvp(api_client, auth(member), meetup, 'going').status_code == 200
    api_client.post(f'{BASE}{meetup.id}/cancel/', {'cancelled': True}, format='json', **auth(host))
    r = api_client.post(f'/api/lite/meetups/{meetup.id}/checkin/', {'code': meetup.checkin_code},
                        format='json', **auth(member))
    assert r.status_code == 400 and r.json()['error'] == '취소된 모임이에요'
    r = put_rsvp(api_client, auth(member), meetup, 'no')
    assert r.status_code == 400 and r.json()['error'] == '취소된 모임이에요'


def test_remove_member(api_client, host, member, auth, make_meetup):
    meetup = make_meetup()
    put_rsvp(api_client, auth(member), meetup, 'going')
    room_id = meetup.room.id
    assert api_client.get(f'/api/lite/rooms/{room_id}/messages/', **auth(member)).status_code == 200
    r = api_client.delete(f'{BASE}{meetup.id}/members/{member.id}/', **auth(host))
    assert r.status_code == 200
    attendee = r.json()['attendees'][0]
    assert attendee['status'] == 'no' and attendee['removed'] is True
    rsvp = Rsvp.objects.get(member=member, meetup=meetup)
    assert rsvp.status == 'no' and rsvp.removed_at is not None
    r = put_rsvp(api_client, auth(member), meetup, 'going')
    assert r.status_code == 403 and r.json()['error'] == '운영자가 내보낸 모임이에요'
    assert api_client.get(f'/api/lite/rooms/{room_id}/messages/', **auth(member)).status_code == 403


def test_remove_member_without_rsvp(api_client, host, member, auth, make_meetup):
    meetup = make_meetup()
    r = api_client.delete(f'{BASE}{meetup.id}/members/{member.id}/', **auth(host))
    assert r.status_code == 404 and r.json()['error'] == '참석 신청한 회원이 아니에요'


def test_delete_message(api_client, host, member, auth, make_meetup):
    meetup = make_meetup()
    other = make_meetup('다른 모임')
    msg = ChatMessage.objects.create(room=meetup.room, member=member, body='지울 말')
    foreign = ChatMessage.objects.create(room=other.room, member=member, body='다른 방')
    url = f'/api/lite/rooms/{meetup.room.id}/messages/'
    assert api_client.delete(f'{url}{foreign.id}/', **auth(host)).status_code == 404
    assert ChatMessage.objects.filter(pk=foreign.pk).exists()
    r = api_client.delete(f'{url}{msg.id}/', **auth(host))
    assert r.status_code == 200 and r.json() == {'deleted': True}
    assert not ChatMessage.objects.filter(pk=msg.pk).exists()


def test_pin_flow(api_client, host, member, auth, make_meetup):
    meetup = make_meetup()
    other = make_meetup('다른 모임')
    put_rsvp(api_client, auth(member), meetup, 'going')
    notice = ChatMessage.objects.create(room=meetup.room, member=host, body='공지')
    foreign = ChatMessage.objects.create(room=other.room, member=host, body='남의 방')
    room_id = meetup.room.id
    pin_url = f'/api/lite/rooms/{room_id}/pin/'
    msgs_url = f'/api/lite/rooms/{room_id}/messages/'

    assert api_client.put(pin_url, {'message_id': foreign.id}, format='json', **auth(host)).status_code == 404
    r = api_client.put(pin_url, {'message_id': notice.id}, format='json', **auth(host))
    assert r.status_code == 200 and r.json()['pinned']['body'] == '공지'

    assert api_client.get(msgs_url, **auth(member)).json()['pinned']['id'] == notice.id
    assert api_client.get(f'{msgs_url}?after=0', **auth(member)).json()['pinned']['id'] == notice.id

    r = api_client.put(pin_url, {'message_id': None}, format='json', **auth(host))
    assert r.json() == {'pinned': None}
    assert api_client.get(msgs_url, **auth(member)).json()['pinned'] is None
    assert api_client.get(f'{msgs_url}?after=0', **auth(member)).json()['pinned'] is None


def test_pin_system_message_and_delete_pinned(api_client, host, member, auth, make_meetup):
    meetup = make_meetup()
    put_rsvp(api_client, auth(member), meetup, 'going')
    system = ChatMessage.objects.filter(room=meetup.room, kind='system').first()
    room_id = meetup.room.id
    r = api_client.put(f'/api/lite/rooms/{room_id}/pin/', {'message_id': system.id}, format='json', **auth(host))
    assert r.status_code == 200 and r.json()['pinned']['kind'] == 'system'
    api_client.delete(f'/api/lite/rooms/{room_id}/messages/{system.id}/', **auth(host))
    assert api_client.get(f'/api/lite/rooms/{room_id}/messages/', **auth(member)).json()['pinned'] is None


def test_delete_meetup(api_client, host, member, auth, make_meetup):
    meetup = make_meetup()
    put_rsvp(api_client, auth(member), meetup, 'going')
    req = MeetupRequest.objects.create(title='등산', created_by=member, status='done', meetup=meetup)
    r = api_client.delete(f'{BASE}{meetup.id}/', **auth(host))
    assert r.status_code == 200 and r.json() == {'deleted': True}
    assert api_client.get(f'{BASE}{meetup.id}/', **auth(host)).status_code == 404
    assert not Rsvp.objects.filter(meetup_id=meetup.id).exists()
    req.refresh_from_db()
    assert req.meetup_id is None and req.status == 'done'


def test_image_url_rules(api_client, host, auth, make_meetup):
    meetup = make_meetup()
    bad = [
        '//evil.com/x.png', 'data:image/png;base64,xx', 'https://', 'https://a b.com',
        '/media//x', '/media/../x', '/media/a\\b', 'https://a.com/x\ny.png', 'https://a.com/x\n',
    ]
    for value in bad:
        assert patch(api_client, auth(host), meetup, image_url=value).status_code == 400, value
    for value in ['HTTP://ok.com/a.png', 'https://ok.com/a.png', '/media/a/b.png', '']:
        assert patch(api_client, auth(host), meetup, image_url=value).status_code == 200, value


def test_locked_meetup_sql_has_no_join(api_client, host, auth, make_meetup):
    meetup = make_meetup()
    with CaptureQueriesContext(connection) as ctx:
        assert patch(api_client, auth(host), meetup, title='새 제목').status_code == 200
        r = api_client.post(f'{BASE}{meetup.id}/cancel/', {'cancelled': True}, format='json', **auth(host))
        assert r.status_code == 200
        r = api_client.delete(f'{BASE}{meetup.id}/members/1/', **auth(host))
    sqls = [q['sql'].upper() for q in ctx.captured_queries]
    # PostgreSQL은 FOR UPDATE가 붙은 쿼리에 OUTER JOIN이 있으면 거부한다. SQLite는 FOR UPDATE를 생략하므로
    # 잠금용 조회(첫 번째 lite_meetup SELECT)에 JOIN이 없는지로 같은 조건을 확인한다.
    locking = [q for q in sqls if 'FOR UPDATE' in q]
    assert not any('OUTER JOIN' in q for q in locking)
    lock_selects = [q for q in sqls if q.startswith('SELECT') and 'FROM "LITE_MEETUP"' in q and 'COUNT' not in q]
    assert lock_selects and 'JOIN' not in lock_selects[0]


def test_remove_member_clears_checkin_and_count(api_client, host, member, auth, make_meetup):
    meetup = make_meetup(days=0)
    put_rsvp(api_client, auth(member), meetup, 'going')
    r = api_client.post(f'/api/lite/meetups/{meetup.id}/checkin/', {'code': meetup.checkin_code}, format='json', **auth(member))
    assert r.status_code == 200
    detail = f'/api/lite/meetups/{meetup.id}/'
    assert api_client.get(detail, **auth(host)).json()['checked_in_count'] == 1
    api_client.delete(f'{BASE}{meetup.id}/members/{member.id}/', **auth(host))
    assert Rsvp.objects.get(member=member, meetup=meetup).checked_in_at is None
    assert api_client.get(detail, **auth(host)).json()['checked_in_count'] == 0
    # 기존 데이터(removed_at만 있고 checked_in_at이 남은 행)도 집계에서 제외된다.
    Rsvp.objects.filter(member=member, meetup=meetup).update(checked_in_at=timezone.now())
    assert api_client.get(detail, **auth(host)).json()['checked_in_count'] == 0
    body = api_client.get(detail, **auth(member)).json()
    assert body['removed'] is True


def test_detail_removed_flag_false_by_default(api_client, member, auth, make_meetup):
    meetup = make_meetup()
    detail = f'/api/lite/meetups/{meetup.id}/'
    assert api_client.get(detail, **auth(member)).json()['removed'] is False
    put_rsvp(api_client, auth(member), meetup, 'going')
    assert api_client.get(detail, **auth(member)).json()['removed'] is False


def test_removed_member_checkin_forbidden(api_client, host, member, auth, make_meetup):
    meetup = make_meetup(days=0)
    put_rsvp(api_client, auth(member), meetup, 'going')
    api_client.delete(f'{BASE}{meetup.id}/members/{member.id}/', **auth(host))
    r = api_client.post(f'/api/lite/meetups/{meetup.id}/checkin/', {'code': meetup.checkin_code}, format='json', **auth(member))
    assert r.status_code == 403 and r.json()['error'] == '운영자가 내보낸 모임이에요'


def test_checkin_cancelled_checked_inside_lock(api_client, host, member, auth, make_meetup):
    meetup = make_meetup(days=0, cancelled_at=timezone.now())
    r = api_client.post(f'/api/lite/meetups/{meetup.id}/checkin/', {'code': 'x'}, format='json', **auth(member))
    assert r.status_code == 400 and r.json()['error'] == '취소된 모임이에요'


def test_remove_member_already_no(api_client, host, member, auth, make_meetup):
    meetup = make_meetup()
    put_rsvp(api_client, auth(member), meetup, 'going')
    put_rsvp(api_client, auth(member), meetup, 'no')
    r = api_client.delete(f'{BASE}{meetup.id}/members/{member.id}/', **auth(host))
    assert r.status_code == 200 and r.json()['attendees'][0]['removed'] is True
    assert Rsvp.objects.get(member=member, meetup=meetup).removed_at is not None


def test_message_delete_and_pin_in_seminar_room(api_client, host, member, auth):
    assert api_client.post('/api/lite/seminar/', **auth(member)).status_code == 200
    room = ChatRoom.objects.get(kind='seminar')
    msg = ChatMessage.objects.create(room=room, member=member, body='주제')
    pin_url = f'/api/lite/rooms/{room.id}/pin/'
    r = api_client.put(pin_url, {'message_id': msg.id}, format='json', **auth(host))
    assert r.status_code == 200 and r.json()['pinned']['id'] == msg.id
    r = api_client.delete(f'/api/lite/rooms/{room.id}/messages/{msg.id}/', **auth(host))
    assert r.status_code == 200
    assert not ChatMessage.objects.filter(pk=msg.pk).exists()


def test_pin_requires_message_id_key_and_types(api_client, host, member, auth, make_meetup):
    meetup = make_meetup()
    msg = ChatMessage.objects.create(room=meetup.room, member=host, body='공지')
    url = f'/api/lite/rooms/{meetup.room.id}/pin/'
    assert api_client.put(url, {}, format='json', **auth(host)).status_code == 400
    for bad in [True, '1', 1.5]:
        assert api_client.put(url, {'message_id': bad}, format='json', **auth(host)).status_code == 400, bad
    assert api_client.put(url, {'message_id': 2**63}, format='json', **auth(host)).status_code == 404
    assert api_client.put(url, {'message_id': msg.id}, format='json', **auth(host)).status_code == 200
    assert api_client.put(url, {'message_id': None}, format='json', **auth(host)).json() == {'pinned': None}


def test_pin_integrity_error_returns_404(api_client, host, auth, make_meetup, monkeypatch):
    meetup = make_meetup()
    msg = ChatMessage.objects.create(room=meetup.room, member=host, body='공지')

    def boom(self, *args, **kwargs):
        raise IntegrityError('fk')

    monkeypatch.setattr(ChatRoom, 'save', boom)
    r = api_client.put(f'/api/lite/rooms/{meetup.room.id}/pin/', {'message_id': msg.id}, format='json', **auth(host))
    assert r.status_code == 404 and r.json()['error'] == '메시지를 찾을 수 없어요'


def test_huge_ids_return_404(api_client, host, member, auth, make_meetup):
    meetup = make_meetup()
    big = 2**63
    assert api_client.get(f'/api/lite/meetups/{big}/', **auth(member)).status_code == 404
    assert api_client.get(f'{BASE}{big}/', **auth(host)).status_code == 404
    assert api_client.delete(f'{BASE}{meetup.id}/members/{big}/', **auth(host)).status_code == 404
    assert api_client.delete(f'/api/lite/rooms/{meetup.room.id}/messages/{big}/', **auth(host)).status_code == 404


def test_missing_meetup_returns_404(api_client, host, auth):
    missing = 999999
    assert api_client.patch(f'{BASE}{missing}/', {'title': 'x'}, format='json', **auth(host)).status_code == 404
    assert api_client.delete(f'{BASE}{missing}/', **auth(host)).status_code == 404
    r = api_client.post(f'{BASE}{missing}/cancel/', {'cancelled': True}, format='json', **auth(host))
    assert r.status_code == 404
    assert api_client.delete(f'{BASE}{missing}/members/1/', **auth(host)).status_code == 404


def test_patch_audience(api_client, host, auth, make_meetup):
    meetup = make_meetup()
    r = patch(api_client, auth(host), meetup, audience='지갑을 이미 써 본 분')
    assert r.status_code == 200 and r.json()['audience'] == '지갑을 이미 써 본 분'
    assert patch(api_client, auth(host), meetup, audience='x' * 101).status_code == 400
    r = patch(api_client, auth(host), meetup, audience='')
    assert r.status_code == 200 and r.json()['audience'] == ''
