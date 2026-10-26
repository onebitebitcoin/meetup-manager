"""모임 썸네일: 원본 이미지를 받아 작은 WebP로 줄여 media에 저장한다. 화면에는 원본 대신 이 파일만 보낸다."""
import hashlib
import io
import logging
from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from PIL import Image, ImageOps, UnidentifiedImageError

from . import linkpreview

logger = logging.getLogger(__name__)

# 화면의 썸네일은 40~88px 정사각형, PC 카드는 높이 150px이라 긴 변 400px이면 충분하다
MAX_SIDE = 400
QUALITY = 78
SOURCE_MAX_BYTES = 15 * 1024 * 1024
THUMB_DIR = 'lite/thumbs'


class ThumbnailError(Exception):
    """썸네일을 만들 수 없을 때. 메시지는 운영자에게 그대로 보여 준다."""


def thumb_name(image_url):
    """같은 원본 주소는 같은 파일 이름을 쓰므로 다시 만들 필요가 없다."""
    digest = hashlib.sha256(image_url.encode('utf-8')).hexdigest()[:20]
    return f'{THUMB_DIR}/{digest}.webp'


def read_media(image_url):
    """/media/로 시작하는 주소는 서버의 media 폴더에서 바로 읽는다(media 폴더 밖은 거부)."""
    root = Path(settings.MEDIA_ROOT).resolve()
    path = (root / image_url[len(settings.MEDIA_URL):]).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        raise ThumbnailError('썸네일 원본 파일을 찾을 수 없어요')
    if path.stat().st_size > SOURCE_MAX_BYTES:
        raise ThumbnailError('썸네일 원본 이미지가 너무 커요(15MB 이하)')
    return path.read_bytes()


def download(image_url):
    try:
        result = linkpreview.fetch(image_url, 'image/', SOURCE_MAX_BYTES)
    except linkpreview.InvalidUrl:
        result = None
    if result is None:
        raise ThumbnailError('썸네일 이미지를 내려받지 못했어요. 공개된 이미지 주소인지 확인해 주세요')
    return result[1]


def shrink(data):
    """이미지 바이트를 긴 변 MAX_SIDE 이하의 WebP 바이트로 바꾼다."""
    try:
        with Image.open(io.BytesIO(data)) as image:
            image = ImageOps.exif_transpose(image)
            image = image.convert('RGBA' if image.mode in ('RGBA', 'LA', 'P') else 'RGB')
            image.thumbnail((MAX_SIDE, MAX_SIDE))
            out = io.BytesIO()
            image.save(out, 'WEBP', quality=QUALITY, method=6)
            return out.getvalue()
    except (UnidentifiedImageError, Image.DecompressionBombError, OSError, ValueError) as exc:
        raise ThumbnailError('썸네일 원본이 이미지 파일이 아니거나 읽을 수 없어요') from exc


def make_thumbnail(image_url):
    """원본 주소로 썸네일을 만들고 그 /media/ 주소를 돌려준다. 이미 만든 파일이 있으면 그대로 쓴다."""
    name = thumb_name(image_url)
    if not default_storage.exists(name):
        source = read_media(image_url) if image_url.startswith(settings.MEDIA_URL) else download(image_url)
        thumb = shrink(source)
        default_storage.save(name, ContentFile(thumb))
        logger.info('LITE 썸네일 생성: %s (%d bytes → %d bytes)', name, len(source), len(thumb))
    return f'{settings.MEDIA_URL}{name}'


def fill_missing_thumbnails():
    """원본 주소는 있는데 썸네일이 없는 모임의 썸네일을 만든다. (만든 수, [(모임 id, 실패 이유)])를 돌려준다."""
    from .models import Meetup

    made, failed = 0, []
    for meetup in Meetup.objects.exclude(image_url='').filter(thumb_url='').order_by('id'):
        try:
            thumb_url = make_thumbnail(meetup.image_url)
        except ThumbnailError as exc:
            logger.warning('LITE 썸네일 실패: meetup=%s url=%s (%s)', meetup.id, meetup.image_url, exc)
            failed.append((meetup.id, str(exc)))
            continue
        Meetup.objects.filter(pk=meetup.pk, image_url=meetup.image_url).update(thumb_url=thumb_url)
        made += 1
    return made, failed
