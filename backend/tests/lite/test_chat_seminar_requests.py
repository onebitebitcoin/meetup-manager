from lite.models import ChatMessage, LiteConfig, MeetupRequest, RequestVote, SeminarRequest


def msgs(client, headers, room_id, after=None):
    url = f'/api/lite/rooms/{room_id}/messages/' + (f'?after={after}' if after is not None else '')
    return client.get(url, **headers)


def send(client, headers, room_id, body):
    return client.post(f'/api/lite/rooms/{room_id}/messages/', {'body': body}, format='json', **headers)


def join(client, headers, meetup, status='going'):
    client.put(f'/api/lite/meetups/{meetup.id}/rsvp/', {'status': status}, format='json', **headers)


# --- 모임 채팅방 ---

def test_meetup_room_access(api_client, member, make_member, host, auth, make_meetup):
    meetup = make_meetup()
    room_id = meetup.room.id
    assert msgs(api_client, auth(member), room_id).status_code == 403
    assert send(api_client, auth(member), room_id, 'hi').status_code == 403
    join(api_client, auth(member), meetup, 'maybe')
    assert msgs(api_client, auth(member), room_id).status_code == 200
    assert send(api_client, auth(member), room_id, 'hi').status_code == 201
    assert msgs(api_client, auth(host), room_id).status_code == 200
    join(api_client, auth(member), meetup, 'no')
    assert msgs(api_client, auth(member), room_id).status_code == 403
    assert msgs(api_client, auth(member), 9999).status_code == 404


def test_messages_after_and_validation(api_client, member, auth, make_meetup):
    meetup = make_meetup()
    join(api_client, auth(member), meetup)
    room_id = meetup.room.id
    r = send(api_client, auth(member), room_id, '  안녕  ')
    assert r.status_code == 201
    msg = r.json()['message']
    assert msg['body'] == '안녕' and msg['kind'] == 'user' and msg['member'] == {'id': member.id, 'name': '민수'}
    got = msgs(api_client, auth(member), room_id, after=msg['id'] - 1).json()['messages']
    assert [m['id'] for m in got] == [msg['id']]
    assert msgs(api_client, auth(member), room_id, after=msg['id']).json()['messages'] == []
    assert msgs(api_client, auth(member), room_id, after='x').status_code == 400
    for body in ['', '   ', 'a' * 1001, None]:
        assert send(api_client, auth(member), room_id, body).status_code == 400
    assert send(api_client, auth(member), room_id, 'a' * 1000).status_code == 201


def test_messages_limit_200_with_after(api_client, host, auth, make_meetup):
    meetup = make_meetup()
    ChatMessage.objects.bulk_create([ChatMessage(room=meetup.room, kind='system', body=str(i)) for i in range(205)])
    assert len(msgs(api_client, auth(host), meetup.room.id, after=0).json()['messages']) == 200


def test_messages_without_after_returns_latest_100_ascending(api_client, host, auth, make_meetup):
    meetup = make_meetup()
    ChatMessage.objects.bulk_create([ChatMessage(room=meetup.room, kind='system', body=str(i)) for i in range(105)])
    ids = [m['id'] for m in msgs(api_client, auth(host), meetup.room.id).json()['messages']]
    expected = list(ChatMessage.objects.filter(room=meetup.room).order_by('-id').values_list('id', flat=True)[:100])
    assert ids == sorted(expected) and len(ids) == 100


# --- 세미나 ---

def start_seminar(client, headers):
    return client.post('/api/lite/seminar/', **headers)


def test_seminar_full_flow(api_client, member, host, auth):
    r = start_seminar(api_client, auth(member))
    assert r.status_code == 200
    card = r.json()['seminar']
    assert card['status'] == 'guide' and card['mode'] is None and card['member']['name'] == '민수'
    room_id = card['room_id']
    cfg = LiteConfig.get()
    guides = list(ChatMessage.objects.filter(room_id=room_id).values_list('kind', 'body'))
    assert guides == [('guide', cfg.seminar_guide_1), ('guide', cfg.seminar_guide_2)]
    assert start_seminar(api_client, auth(member)).json()['seminar']['id'] == card['id']
    assert ChatMessage.objects.filter(room_id=room_id).count() == 2

    # mode 선택 전 메시지는 접수되지 않는다
    send(api_client, auth(member), room_id, '질문')
    assert SeminarRequest.objects.get().status == 'guide'

    r = api_client.post('/api/lite/seminar/mode/', {'mode': 'online'}, format='json', **auth(member))
    assert r.status_code == 200 and r.json()['seminar']['mode'] == 'online'
    last_two = list(ChatMessage.objects.filter(room_id=room_id).order_by('-id')[:2].values_list('kind', 'body'))
    assert last_two == [('guide', cfg.seminar_guide_3), ('user', '온라인')]

    send(api_client, auth(member), room_id, 'AI 주제, 토요일 3시')
    seminar = SeminarRequest.objects.get()
    assert seminar.status == 'received' and seminar.topic == 'AI 주제, 토요일 3시'
    assert ChatMessage.objects.filter(room_id=room_id).last().body == cfg.seminar_guide_4

    # 접수 이후 메시지는 상태를 바꾸지 않는다
    send(api_client, auth(member), room_id, '추가')
    assert SeminarRequest.objects.get().topic == 'AI 주제, 토요일 3시'

    home = api_client.get('/api/lite/home/', **auth(host)).json()
    assert [s['id'] for s in home['seminars']] == [seminar.id]
    assert api_client.get('/api/lite/home/', **auth(member)).json()['my_seminar']['status'] == 'received'
    assert api_client.get('/api/lite/home/', **auth(member)).json()['seminars'] == []

    r = api_client.post(f'/api/lite/seminars/{seminar.id}/confirm/', **auth(host))
    assert r.status_code == 200 and r.json()['seminar']['status'] == 'confirmed'
    assert r.json()['seminar']['last_message'] == '일정 확정'
    api_client.post(f'/api/lite/seminars/{seminar.id}/confirm/', **auth(host))
    assert ChatMessage.objects.filter(room_id=room_id, body='일정 확정').count() == 1


def test_seminar_host_message_does_not_receive(api_client, member, host, auth):
    room_id = start_seminar(api_client, auth(member)).json()['seminar']['room_id']
    api_client.post('/api/lite/seminar/mode/', {'mode': 'offline'}, format='json', **auth(member))
    assert send(api_client, auth(host), room_id, '안내').status_code == 201
    assert SeminarRequest.objects.get().status == 'guide'


def test_seminar_room_access(api_client, member, make_member, host, auth):
    room_id = start_seminar(api_client, auth(member)).json()['seminar']['room_id']
    other = make_member('타인')
    assert msgs(api_client, auth(other), room_id).status_code == 403
    assert send(api_client, auth(other), room_id, 'x').status_code == 403
    assert msgs(api_client, auth(host), room_id).status_code == 200


def test_seminar_mode_errors(api_client, member, auth):
    r = api_client.post('/api/lite/seminar/mode/', {'mode': 'online'}, format='json', **auth(member))
    assert r.status_code == 404
    start_seminar(api_client, auth(member))
    r = api_client.post('/api/lite/seminar/mode/', {'mode': 'zoom'}, format='json', **auth(member))
    assert r.status_code == 400


def test_seminar_confirm_permissions(api_client, member, auth):
    start_seminar(api_client, auth(member))
    sid = SeminarRequest.objects.get().id
    assert api_client.post(f'/api/lite/seminars/{sid}/confirm/', **auth(member)).status_code == 403
    assert api_client.post('/api/lite/seminars/999/confirm/', **auth(member)).status_code == 403


def test_seminar_confirm_not_found(api_client, host, auth):
    assert api_client.post('/api/lite/seminars/999/confirm/', **auth(host)).status_code == 404


# --- 요청 ---

def create_request(client, headers, title='등산 가요', period='any'):
    return client.post('/api/lite/requests/', {'title': title, 'preferred_period': period}, format='json', **headers)


def test_create_request_auto_vote(api_client, member, auth):
    r = create_request(api_client, auth(member), period='next_month')
    assert r.status_code == 201
    card = r.json()['request']
    assert card['vote_count'] == 1 and card['voted'] is True and card['threshold'] == 5
    assert card['status'] == 'open' and card['meetup_id'] is None and card['preferred_period'] == 'next_month'


def test_create_request_validation(api_client, member, auth):
    assert create_request(api_client, auth(member), title='').status_code == 400
    assert create_request(api_client, auth(member), title='x' * 61).status_code == 400
    assert create_request(api_client, auth(member), period='never').status_code == 400


def test_vote_toggle_and_list_order(api_client, member, make_member, auth):
    other = make_member('다른이')
    first = create_request(api_client, auth(member), 'A').json()['request']['id']
    second = create_request(api_client, auth(member), 'B').json()['request']['id']
    r = api_client.post(f'/api/lite/requests/{second}/vote/', **auth(other))
    assert r.json()['request']['vote_count'] == 2 and r.json()['request']['voted'] is True
    r = api_client.post(f'/api/lite/requests/{first}/vote/', **auth(member))
    assert r.json()['request']['vote_count'] == 0 and r.json()['request']['voted'] is False
    r = api_client.post(f'/api/lite/requests/{first}/vote/', **auth(member))
    assert r.json()['request']['vote_count'] == 1
    listing = api_client.get('/api/lite/requests/', **auth(other)).json()['requests']
    assert [x['title'] for x in listing] == ['B', 'A']


def test_done_requests_listed_last_and_not_votable(api_client, member, auth):
    done = MeetupRequest.objects.create(title='끝', created_by=member, status='done')
    RequestVote.objects.create(request=done, member=member)
    create_request(api_client, auth(member), '열림')
    listing = api_client.get('/api/lite/requests/', **auth(member)).json()['requests']
    assert [x['title'] for x in listing] == ['열림', '끝']
    assert api_client.post(f'/api/lite/requests/{done.id}/vote/', **auth(member)).status_code == 400
    assert api_client.post('/api/lite/requests/999/vote/', **auth(member)).status_code == 404
