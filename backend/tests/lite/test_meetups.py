from datetime import timedelta

from django.utils import timezone

from lite.models import ChatMessage, MeetupRequest, RequestVote, Rsvp
from lite.services import KST


def rsvp(client, headers, meetup, status):
    return client.put(f'/api/lite/meetups/{meetup.id}/rsvp/', {'status': status}, format='json', **headers)


def create_payload(**over):
    data = {
        'title': '보드게임', 'starts_at': (timezone.now() + timedelta(days=2)).isoformat(),
        'location': '홍대', 'capacity': 8,
    }
    data.update(over)
    return data


def test_create_meetup(api_client, host, auth):
    r = api_client.post('/api/lite/meetups/', create_payload(description='설명'), format='json', **auth(host))
    assert r.status_code == 201
    card = r.json()['meetup']
    assert card['title'] == '보드게임' and card['going_count'] == 0 and card['from_request'] is False
    assert card['room_id']


def test_create_meetup_from_request(api_client, host, member, auth):
    req = MeetupRequest.objects.create(title='등산', created_by=member)
    RequestVote.objects.create(request=req, member=member)
    r = api_client.post('/api/lite/meetups/', create_payload(request_id=req.id), format='json', **auth(host))
    assert r.status_code == 201 and r.json()['meetup']['from_request'] is True
    req.refresh_from_db()
    assert req.status == 'done' and req.meetup_id == r.json()['meetup']['id']
    msg = ChatMessage.objects.get(room_id=r.json()['meetup']['room_id'])
    assert msg.kind == 'system' and msg.body == '요청으로 열린 모임이에요 · 1명에게 알림'
    again = api_client.post('/api/lite/meetups/', create_payload(request_id=req.id), format='json', **auth(host))
    assert again.status_code == 400


def test_create_meetup_unknown_request(api_client, host, auth):
    r = api_client.post('/api/lite/meetups/', create_payload(request_id=999), format='json', **auth(host))
    assert r.status_code == 404


def test_create_meetup_validation(api_client, host, auth):
    for over in [{'title': ''}, {'title': 'x' * 81}, {'capacity': 1}, {'capacity': 501}, {'capacity': 'abc'},
                 {'starts_at': 'bad'}, {'location': ''}]:
        r = api_client.post('/api/lite/meetups/', create_payload(**over), format='json', **auth(host))
        assert r.status_code == 400, over
        assert r.json()['error']


def test_home_filters_past_and_orders(api_client, member, auth, make_meetup):
    make_meetup('나중', days=3)
    make_meetup('먼저', days=1)
    make_meetup('어제', days=-2)
    r = api_client.get('/api/lite/home/', **auth(member))
    assert r.status_code == 200
    body = r.json()
    assert [m['title'] for m in body['meetups']] == ['먼저', '나중']
    assert body['my_seminar'] is None and body['seminars'] == [] and body['ready_request_count'] == 0


def test_home_card_includes_thumbnail_or_null(api_client, member, auth, make_meetup):
    with_image = make_meetup('이미지', days=1)
    with_image.image_url = '/media/meetups/a.png'
    with_image.save(update_fields=['image_url'])
    make_meetup('없음', days=2)
    cards = api_client.get('/api/lite/home/', **auth(member)).json()['meetups']
    assert [c['image_url'] for c in cards] == ['/media/meetups/a.png', None]


def test_home_keeps_meetup_earlier_today(api_client, member, auth, make_meetup):
    meetup = make_meetup('오전 모임')
    now_kst = timezone.now().astimezone(KST)
    meetup.starts_at = now_kst.replace(hour=0, minute=1, second=0, microsecond=0)
    meetup.save()
    r = api_client.get('/api/lite/home/', **auth(member))
    assert [m['title'] for m in r.json()['meetups']] == ['오전 모임']
    assert r.json()['meetups'][0]['is_today'] is True


def test_home_ready_request_count(api_client, member, make_member, auth):
    req = MeetupRequest.objects.create(title='r', created_by=member)
    for i in range(5):
        RequestVote.objects.create(request=req, member=make_member(f'v{i}'))
    assert api_client.get('/api/lite/home/', **auth(member)).json()['ready_request_count'] == 1


def test_rsvp_flow_and_messages(api_client, member, auth, make_meetup):
    meetup = make_meetup()
    r = rsvp(api_client, auth(member), meetup, 'going')
    assert r.status_code == 200
    assert r.json()['meetup']['my_status'] == 'going' and r.json()['meetup']['going_count'] == 1
    bodies = list(ChatMessage.objects.filter(room=meetup.room).values_list('kind', 'body'))
    assert bodies == [('system', '민수님 참석'), ('guide', '신청 완료! 공지는 여기서 안내해요.')]
    rsvp(api_client, auth(member), meetup, 'going')
    assert ChatMessage.objects.filter(room=meetup.room).count() == 2
    r = rsvp(api_client, auth(member), meetup, 'maybe')
    assert r.json()['meetup']['going_count'] == 0 and r.json()['meetup']['maybe_count'] == 1
    assert ChatMessage.objects.filter(room=meetup.room).count() == 3
    assert ChatMessage.objects.filter(room=meetup.room).last().body == '민수님 미정'
    rsvp(api_client, auth(member), meetup, 'no')
    assert Rsvp.objects.get(member=member).status == 'no'


def test_rsvp_invalid_status(api_client, member, auth, make_meetup):
    assert rsvp(api_client, auth(member), make_meetup(), 'zzz').status_code == 400


def test_rsvp_unknown_meetup(api_client, member, auth):
    r = api_client.put('/api/lite/meetups/999/rsvp/', {'status': 'going'}, format='json', **auth(member))
    assert r.status_code == 404


def test_rsvp_capacity_exceeded(api_client, member, make_member, auth, make_meetup):
    meetup = make_meetup(capacity=2)
    for n in ('a', 'b'):
        assert rsvp(api_client, auth(make_member(n)), meetup, 'going').status_code == 200
    r = rsvp(api_client, auth(member), meetup, 'going')
    assert r.status_code == 409 and r.json() == {'error': '정원이 찼어요'}
    assert rsvp(api_client, auth(member), meetup, 'maybe').status_code == 200
    assert not Rsvp.objects.filter(member=member, status='going').exists()


def test_detail_checkin_code_visibility(api_client, member, host, auth, make_meetup):
    today = make_meetup(days=0)
    today.starts_at = timezone.now()
    today.save()
    future = make_meetup(days=3)
    assert api_client.get(f'/api/lite/meetups/{today.id}/', **auth(host)).json()['checkin_code'] == today.checkin_code
    assert api_client.get(f'/api/lite/meetups/{future.id}/', **auth(host)).json()['checkin_code'] is None
    body = api_client.get(f'/api/lite/meetups/{today.id}/', **auth(member)).json()
    assert body['checkin_code'] is None and body['checked_in'] is False and body['checked_in_count'] == 0
    assert api_client.get('/api/lite/meetups/999/', **auth(member)).status_code == 404


def _today_meetup(make_meetup):
    meetup = make_meetup(days=0)
    meetup.starts_at = timezone.now()
    meetup.save()
    return meetup


def checkin(client, headers, meetup, code):
    return client.post(f'/api/lite/meetups/{meetup.id}/checkin/', {'code': code}, format='json', **headers)


def test_checkin_success(api_client, member, auth, make_meetup):
    meetup = _today_meetup(make_meetup)
    rsvp(api_client, auth(member), meetup, 'going')
    r = checkin(api_client, auth(member), meetup, meetup.checkin_code)
    assert r.status_code == 200 and r.json() == {'checked_in': True}
    assert ChatMessage.objects.filter(room=meetup.room, body='민수님 도착').count() == 1
    checkin(api_client, auth(member), meetup, meetup.checkin_code)
    assert ChatMessage.objects.filter(room=meetup.room, body='민수님 도착').count() == 1
    detail = api_client.get(f'/api/lite/meetups/{meetup.id}/', **auth(member)).json()
    assert detail['checked_in'] is True and detail['checked_in_count'] == 1


def test_checkin_wrong_code(api_client, member, auth, make_meetup):
    meetup = _today_meetup(make_meetup)
    rsvp(api_client, auth(member), meetup, 'maybe')
    wrong = '0000' if meetup.checkin_code != '0000' else '1111'
    r = checkin(api_client, auth(member), meetup, wrong)
    assert r.status_code == 400 and r.json() == {'error': '코드가 달라요'}


def test_checkin_not_today(api_client, member, auth, make_meetup):
    meetup = make_meetup(days=3)
    rsvp(api_client, auth(member), meetup, 'going')
    assert checkin(api_client, auth(member), meetup, meetup.checkin_code).status_code == 400


def test_checkin_requires_rsvp(api_client, member, auth, make_meetup):
    meetup = _today_meetup(make_meetup)
    assert checkin(api_client, auth(member), meetup, meetup.checkin_code).status_code == 403
    rsvp(api_client, auth(member), meetup, 'no')
    assert checkin(api_client, auth(member), meetup, meetup.checkin_code).status_code == 403


def test_create_meetup_with_audience_and_detail_shows_info(api_client, host, member, auth):
    payload = create_payload(description='멀티시그 지갑을 직접 만들어 봅니다', audience='  비트코인을 처음 접하는 분  ')
    r = api_client.post('/api/lite/meetups/', payload, format='json', **auth(host))
    assert r.status_code == 201
    meetup_id = r.json()['meetup']['id']

    # 신청하지 않은 회원과 이름 없는 방문자도 상세 안내(내용, 대상)를 본다
    for headers in (auth(member), {}):
        body = api_client.get(f'/api/lite/meetups/{meetup_id}/', **headers).json()
        assert body['description'] == '멀티시그 지갑을 직접 만들어 봅니다'
        assert body['audience'] == '비트코인을 처음 접하는 분'


def test_create_meetup_audience_validation(api_client, host, auth):
    for bad in ['x' * 101, 5]:
        r = api_client.post('/api/lite/meetups/', create_payload(audience=bad), format='json', **auth(host))
        assert r.status_code == 400, bad


def test_detail_without_audience_is_empty_string(api_client, member, auth, make_meetup):
    body = api_client.get(f'/api/lite/meetups/{make_meetup().id}/', **auth(member)).json()
    assert body['audience'] == ''
