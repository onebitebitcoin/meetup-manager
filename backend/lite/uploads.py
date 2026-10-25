"""채팅 첨부 파일 검증. 계약은 SPEC.md 11.4.1을 따른다."""
import os
import re
import unicodedata
import uuid

from PIL import Image, UnidentifiedImageError

from .models import ChatMessage
from .views.base import ApiError

MAX_UPLOAD_SIZE = 10 * 1024 * 1024
MAX_NAME_LENGTH = 120
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
BLOCKED_EXTENSIONS = {
    '.html', '.htm', '.xhtml', '.svg', '.svgz', '.xml', '.js', '.mjs',
    '.exe', '.bat', '.cmd', '.sh', '.php', '.jsp', '.asp', '.aspx',
}
UNSAFE_NAME_CHARS = re.compile(r'[/\\\x00-\x1f\x7f]')


def clean_filename(name):
    name = unicodedata.normalize('NFKC', name or '')
    return UNSAFE_NAME_CHARS.sub('', name).strip()[:MAX_NAME_LENGTH]


def validate_attachment(upload):
    """검증을 통과한 첨부 정보(dict)를 돌려준다. 실패하면 ApiError."""
    if upload is None or not upload.size:
        raise ApiError('파일을 선택해 주세요')
    if upload.size > MAX_UPLOAD_SIZE:
        raise ApiError('파일은 10MB까지 올릴 수 있어요', 413)
    original_name = upload.name or ''
    ext = os.path.splitext(original_name)[1].lower()
    if ext in IMAGE_EXTENSIONS:
        try:
            Image.open(upload).verify()
        except (UnidentifiedImageError, Image.DecompressionBombError, OSError, SyntaxError, ValueError):
            raise ApiError('이미지 파일이 올바르지 않아요') from None
        finally:
            upload.seek(0)
        kind = ChatMessage.AttachmentKind.IMAGE
    elif not ext or ext in BLOCKED_EXTENSIONS:
        raise ApiError('올릴 수 없는 파일 형식이에요')
    else:
        kind = ChatMessage.AttachmentKind.FILE
    upload.name = uuid.uuid4().hex + ext
    return {
        'attachment_name': clean_filename(original_name),
        'attachment_size': upload.size,
        'attachment_kind': kind,
    }
