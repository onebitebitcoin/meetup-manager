import io
from datetime import timedelta
from unittest import mock

import pytest
from django.core.management import call_command
from django.utils import timezone
from PIL import Image

from lite import linkpreview, thumbnails
from lite.models import Meetup
from lite.thumbnails import ThumbnailError, fill_missing_thumbnails, make_thumbnail


@pytest.fixture
def fake_thumbnails():
    """conftest의 가짜 썸네일을 끄고 실제로 만든다."""


@pytest.fixture
def media(settings, tmp_path):
    settings.MEDIA_ROOT = str(tmp_path)
    settings.MEDIA_URL = '/media/'
    return tmp_path


def png_bytes(size=(2000, 1000), color=(200, 120, 30)):
    out = io.BytesIO()
    Image.new('RGB', size, color).save(out, 'PNG')
    return out.getvalue()


def put(media, rel, data):
    path = media / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return f'/media/{rel}'


def open_thumb(media, url):
    return Image.open(media / url[len('/media/'):])


def test_media_원본을_긴_변_400px_webp로_줄인다(media):
    source = png_bytes()
    url = make_thumbnail(put(media, 'meetups/big.png', source))
    assert url.startswith('/media/lite/thumbs/') and url.endswith('.webp')
    with open_thumb(media, url) as image:
        assert image.format == 'WEBP' and image.size == (400, 200)
    assert (media / url[len('/media/'):]).stat().st_size < len(source)


def test_작은_이미지는_키우지_않는다(media):
    url = make_thumbnail(put(media, 'meetups/small.png', png_bytes((120, 80))))
    with open_thumb(media, url) as image:
        assert image.size == (120, 80)


def test_같은_원본은_다시_만들지_않는다(media):
    source_url = put(media, 'meetups/a.png', png_bytes())
    first = make_thumbnail(source_url)
    (media / 'meetups/a.png').unlink()
    assert make_thumbnail(source_url) == first


@pytest.mark.parametrize('rel', ['../outside.png', 'meetups/none.png'])
def test_media_폴더_밖이나_없는_파일은_거부한다(media, rel):
    (media.parent / 'outside.png').write_bytes(png_bytes())
    with pytest.raises(ThumbnailError):
        make_thumbnail(f'/media/{rel}')


def test_이미지가_아니면_거부한다(media):
    with pytest.raises(ThumbnailError):
        make_thumbnail(put(media, 'meetups/fake.png', b'not an image'))


def test_외부_주소는_안전한_fetch로_이미지만_받는다(media):
    with mock.patch.object(linkpreview, 'fetch', return_value=('image/png', png_bytes())) as fetch:
        url = make_thumbnail('https://example.com/a.png')
    fetch.assert_called_once_with('https://example.com/a.png', 'image/', thumbnails.SOURCE_MAX_BYTES)
    with open_thumb(media, url) as image:
        assert image.size == (400, 200)


def test_외부_주소를_받지_못하면_오류(media):
    with mock.patch.object(linkpreview, 'fetch', return_value=None), pytest.raises(ThumbnailError):
        make_thumbnail('https://example.com/a.png')


def test_fetch는_요청한_형식이_아니면_본문을_버린다():
    with mock.patch.object(linkpreview, 'resolve_host', return_value=['93.184.216.34']), \
            mock.patch.object(linkpreview, 'send_request', return_value=(200, {'content-type': 'text/html'}, b'')):
        assert linkpreview.fetch('https://example.com/a.png', 'image/') is None
    with mock.patch.object(linkpreview, 'resolve_host', return_value=['93.184.216.34']), \
            mock.patch.object(linkpreview, 'send_request', return_value=(200, {'content-type': 'image/png'}, b'x')):
        assert linkpreview.fetch('https://example.com/a.png', 'image/') == ('image/png', b'x')


def make_meetup(image_url):
    return Meetup.objects.create(
        title='모임', starts_at=timezone.now() + timedelta(days=1), location='강남', capacity=5, image_url=image_url,
    )


def test_빈_썸네일을_채우고_실패는_따로_알린다(db, media):
    ok = make_meetup(put(media, 'meetups/ok.png', png_bytes()))
    broken = make_meetup('/media/meetups/missing.png')
    make_meetup('')
    made, failed = fill_missing_thumbnails()
    assert made == 1 and [meetup_id for meetup_id, _ in failed] == [broken.id]
    ok.refresh_from_db()
    assert ok.thumb_url.startswith('/media/lite/thumbs/')
    assert fill_missing_thumbnails() == (0, failed)


def test_명령어로_썸네일을_채운다(db, media, capsys):
    meetup = make_meetup(put(media, 'meetups/ok.png', png_bytes()))
    call_command('make_lite_thumbnails')
    meetup.refresh_from_db()
    assert meetup.thumb_url and '썸네일 만듦 1개' in capsys.readouterr().out
