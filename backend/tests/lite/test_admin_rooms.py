
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from lite.models import ChatMessage, RoomRead, SeminarRequest

URL = '/api/lite/admin/rooms/'


def say(room, member, body='안녕', **kw):
    return ChatMessage.objects.create(room=room, member=member, kind=ChatMessage.Kind.USER, body=body, **kw)


def get(client, headers):
    return client.get(URL, **headers)


def test_권한(api_client, member, host, auth):
    assert get(api_client, {}).status_code == 401
    assert get(api_client, auth(member)).status_code == 403
    r = get(api_client, auth(host))
    assert r.status_code == 200 and r.json() == {'rooms': []}


def test_모임과_세미나_방을_정렬해_돌려준다(api_client, host, make_member, make_meetup, auth):
    guest = make_member('손님')
    old = make_meetup('오래된 방')
    new = make_meetup('최근 방')
    quiet = make_meetup('조용한 방')
    seminar = SeminarRequest.objects.create(member=guest)
    say(old.room, guest, 'old')
    say(seminar.room, guest, 'sem')
    say(new.room, guest, 'new')
    r = get(api_client, auth(host)).json()['rooms']
    assert [x['room_id'] for x in r] == [new.room.id, seminar.room.id, old.room.id, quiet.room.id]
    assert r[0]['kind'] == 'meetup' and r[0]['meetup_id'] == new.id and r[0]['title'] == '최근 방'
    assert r[1]['kind'] == 'seminar' and r[1]['seminar_id'] == seminar.id and r[1]['title'] == '1:1 · 손님'
    assert r[0]['last_message']['body'] == 'new' and r[0]['unread_count'] == 1
    assert r[3]['last_message'] is None and r[3]['unread_count'] == 0


def test_취소된_모임과_지난_모임도_포함한다(api_client, host, make_meetup, auth):
    cancelled = make_meetup('취소', days=1)
    cancelled.cancelled_at = timezone.now()
    cancelled.save()
    past = make_meetup('지난', days=-30)
    rooms = {x['title']: x for x in get(api_client, auth(host)).json()['rooms']}
    assert rooms['취소']['cancelled'] is True and rooms['지난']['cancelled'] is False
    assert past.room.id == rooms['지난']['room_id']


def test_마지막_메시지는_사람이_쓴_것만_보고_첨부만_있으면_본문이_빈다(api_client, host, make_member, make_meetup, auth):
    guest = make_member('손님')
    meetup = make_meetup()
    say(meetup.room, guest, '사람 말')
    say(meetup.room, guest, '', attachment='lite/chat/x.png', attachment_kind='image')
    ChatMessage.objects.create(room=meetup.room, kind=ChatMessage.Kind.SYSTEM, body='시스템')
    room = get(api_client, auth(host)).json()['rooms'][0]
    assert room['last_message']['body'] == ''
    assert room['unread_count'] == 2


def test_안_읽은_수는_읽은_위치와_내_메시지를_뺀다(api_client, host, make_member, make_meetup, auth):
    guest = make_member('손님')
    meetup = make_meetup()
    first = say(meetup.room, guest, '1')
    say(meetup.room, host, '내가 쓴 것')
    say(meetup.room, guest, '2')
    RoomRead.objects.create(member=host, room=meetup.room, last_read_id=first.id)
    assert get(api_client, auth(host)).json()['rooms'][0]['unread_count'] == 1


def test_쿼리_수는_방_수에_비례하지_않는다(api_client, host, make_member, make_meetup, auth):
    guest = make_member('손님')

    def count():
        with CaptureQueriesContext(connection) as ctx:
            assert get(api_client, auth(host)).status_code == 200
        return len(ctx)

    make_meetup('하나')
    base = count()
    for i in range(6):
        m = make_meetup(f'모임{i}', days=i + 2)
        say(m.room, guest, 'hi')
        SeminarRequest.objects.create(member=make_member(f'회원{i}'))
    assert count() == base


def test_100개로_제한한다(api_client, host, make_meetup, auth):
    for i in range(103):
        make_meetup(f'm{i}', days=i + 1)
    assert len(get(api_client, auth(host)).json()['rooms']) == 100
