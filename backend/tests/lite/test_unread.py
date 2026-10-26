from lite.models import ChatMessage


def detail(client, headers, meetup):
    return client.get(f'/api/lite/meetups/{meetup.id}/', **headers).json()


def join(client, headers, meetup):
    assert client.put(f'/api/lite/meetups/{meetup.id}/rsvp/', {'status': 'going'}, format='json', **headers).status_code == 200


def talk(meetup, member, body='공지'):
    return ChatMessage.objects.create(room=meetup.room, member=member, kind=ChatMessage.Kind.USER, body=body)


def open_room(client, headers, meetup, **params):
    return client.get(f'/api/lite/rooms/{meetup.room.id}/messages/', params, **headers)


def test_안_읽은_대화는_남이_쓴_메시지만_센다(api_client, member, host, auth, make_meetup):
    meetup = make_meetup()
    join(api_client, auth(member), meetup)
    talk(meetup, host, '첫 공지')
    talk(meetup, host, '둘째 공지')
    talk(meetup, member, '내가 쓴 말')
    ChatMessage.objects.create(room=meetup.room, kind=ChatMessage.Kind.SYSTEM, body='누군가 참석')
    assert detail(api_client, auth(member), meetup)['unread_count'] == 2


def test_채팅방을_열면_읽음으로_바뀌고_새_메시지만_다시_센다(api_client, member, host, auth, make_meetup):
    meetup = make_meetup()
    join(api_client, auth(member), meetup)
    talk(meetup, host)
    assert open_room(api_client, auth(member), meetup).status_code == 200
    assert detail(api_client, auth(member), meetup)['unread_count'] == 0

    newer = talk(meetup, host, '새 공지')
    assert detail(api_client, auth(member), meetup)['unread_count'] == 1
    # 폴링(after)으로 새 메시지를 받아도 읽음이 된다
    open_room(api_client, auth(member), meetup, after=newer.id - 1)
    assert detail(api_client, auth(member), meetup)['unread_count'] == 0


def test_이전_메시지를_불러와도_읽은_위치는_뒤로_가지_않는다(api_client, member, host, auth, make_meetup):
    meetup = make_meetup()
    join(api_client, auth(member), meetup)
    first = talk(meetup, host)
    talk(meetup, host)
    open_room(api_client, auth(member), meetup)
    open_room(api_client, auth(member), meetup, before=first.id + 1)
    assert detail(api_client, auth(member), meetup)['unread_count'] == 0


def test_신청하지_않은_사람과_방문자는_0이다(api_client, member, host, auth, make_meetup):
    meetup = make_meetup()
    talk(meetup, host)
    assert detail(api_client, auth(member), meetup)['unread_count'] == 0
    assert api_client.get(f'/api/lite/meetups/{meetup.id}/').json()['unread_count'] == 0


def test_운영자도_안_읽은_대화를_센다(api_client, member, host, auth, make_meetup):
    meetup = make_meetup()
    join(api_client, auth(member), meetup)
    talk(meetup, member, '질문 있어요')
    assert detail(api_client, auth(host), meetup)['unread_count'] == 1
