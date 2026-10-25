import hashlib

from django.core.cache import cache
from rest_framework.response import Response

from ..linkpreview import InvalidUrl, fetch_preview
from ..throttles import LinkPreviewThrottle
from .base import ApiError, LiteView

CACHE_SECONDS = 24 * 60 * 60
MAX_URL_LENGTH = 2000
MISS = 'none'  # 캐시에서 None(미리보기 없음)과 키 없음을 구분하기 위한 표식


class LinkPreviewView(LiteView):
    throttle_classes = [LinkPreviewThrottle]

    def get(self, request):
        url = request.query_params.get('url', '').strip()
        if not url or len(url) > MAX_URL_LENGTH:
            raise ApiError('링크 주소가 올바르지 않아요')
        key = 'lite_link_preview_' + hashlib.sha256(url.encode('utf-8')).hexdigest()
        cached = cache.get(key, MISS)
        if cached != MISS:
            return Response({'preview': cached})
        try:
            preview = fetch_preview(url)
        except InvalidUrl:
            raise ApiError('링크 주소가 올바르지 않아요') from None
        cache.set(key, preview, CACHE_SECONDS)
        return Response({'preview': preview})
