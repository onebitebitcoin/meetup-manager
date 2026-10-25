import io
import os

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from lite.models import ChatMessage

from .test_chat_seminar_requests import join, msgs, send

MAX_SIZE = 10 * 1024 * 1024


@pytest.fixture(autouse=True)
def tmp_media(settings, tmp_path):
    settings.MEDIA_ROOT = str(tmp_path)
    return tmp_path


def png_bytes():
    buf = io.BytesIO()
    Image.new('RGB', (4, 4), 'red').save(buf, 'PNG')
    return buf.getvalue()


def upload(client, headers, room_id, file=None, body=None):
    data = {}
    if file is not None:
        data['file'] = file
    if body is not None:
        data['body'] = body
    return client.post(f'/api/lite/rooms/{room_id}/files/', data, format='multipart', **headers)


@pytest.fixture
def room(api_client, member, auth, make_meetup):
    meetup = make_meetup()
    join(api_client, auth(member), meetup)
    return meetup.room


def test_image_upload(api_client, member, auth, room, tmp_media):
    f = SimpleUploadedFile('내 사진.PNG', png_bytes(), content_type='image/png')
    r = upload(api_client, auth(member), room.id, f, body='봐요')
    assert r.status_code == 201
    msg = r.json()['message']
    att = msg['attachment']
    assert att['kind'] == 'image' and att['name'] == '내 사진.PNG'
    assert att['url'].startswith('/media/lite/chat/') and att['url'].endswith('.png')
    assert '내 사진' not in att['url']
    assert att['size'] == len(png_bytes())
    assert msg['body'] == '봐요'
    assert len(list(tmp_media.rglob('*.png'))) == 1


def test_file_upload_without_body(api_client, member, auth, room):
    f = SimpleUploadedFile('안내문.pdf', b'%PDF-1.4 test', content_type='application/pdf')
    r = upload(api_client, auth(member), room.id, f)
    assert r.status_code == 201
    msg = r.json()['message']
    assert msg['body'] == '' and msg['attachment']['kind'] == 'file'
    assert msg['attachment']['name'] == '안내문.pdf'


def test_too_large_413(api_client, member, auth, room):
    f = SimpleUploadedFile('big.pdf', b'0' * (MAX_SIZE + 1))
    r = upload(api_client, auth(member), room.id, f)
    assert r.status_code == 413
    assert r.json()['error'] == '파일은 10MB까지 올릴 수 있어요'
    assert not ChatMessage.objects.filter(room=room, kind='user').exists()


@pytest.mark.parametrize('name', ['a.svg', 'a.HTML', 'a.js', 'a.php', 'noext'])
def test_dangerous_extension_400(api_client, member, auth, room, name):
    r = upload(api_client, auth(member), room.id, SimpleUploadedFile(name, b'<script>1</script>'))
    assert r.status_code == 400
    assert r.json()['error'] == '올릴 수 없는 파일 형식이에요'


def test_fake_image_400(api_client, member, auth, room):
    r = upload(api_client, auth(member), room.id, SimpleUploadedFile('a.png', b'not an image'))
    assert r.status_code == 400
    assert r.json()['error'] == '이미지 파일이 올바르지 않아요'


def test_missing_or_empty_file_400(api_client, member, auth, room):
    assert upload(api_client, auth(member), room.id).status_code == 400
    r = upload(api_client, auth(member), room.id, SimpleUploadedFile('a.pdf', b''))
    assert r.status_code == 400 and r.json()['error'] == '파일을 선택해 주세요'


def test_body_too_long_400(api_client, member, auth, room):
    f = SimpleUploadedFile('a.pdf', b'x')
    assert upload(api_client, auth(member), room.id, f, body='a' * 1001).status_code == 400


def test_non_member_403(api_client, make_member, auth, room):
    other = make_member('낯선이')
    r = upload(api_client, auth(other), room.id, SimpleUploadedFile('a.pdf', b'x'))
    assert r.status_code == 403


def test_polling_includes_attachment_and_text_is_null(api_client, member, auth, room):
    send(api_client, auth(member), room.id, '텍스트')
    upload(api_client, auth(member), room.id, SimpleUploadedFile('a.pdf', b'x'))
    got = msgs(api_client, auth(member), room.id).json()['messages']
    users = [m for m in got if m['kind'] == 'user']
    assert users[0]['attachment'] is None
    assert users[1]['attachment']['name'] == 'a.pdf'
    assert all(m['attachment'] is None for m in got if m['kind'] != 'user')


def test_delete_message_removes_file(api_client, member, host, auth, room, tmp_media):
    upload(api_client, auth(member), room.id, SimpleUploadedFile('a.pdf', b'x'))
    msg = ChatMessage.objects.get(room=room, kind='user')
    path = msg.attachment.path
    assert os.path.exists(path)
    r = api_client.delete(f'/api/lite/rooms/{room.id}/messages/{msg.id}/', **auth(host))
    assert r.status_code in (200, 204)
    assert not os.path.exists(path)
