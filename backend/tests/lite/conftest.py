import hashlib
from datetime import timedelta
from unittest import mock

import pytest
from django.core.cache import cache
from django.utils import timezone

from lite.models import Meetup, Member


@pytest.fixture(autouse=True)
def clear_throttle_cache():
    cache.clear()
    yield
    cache.clear()


@pytest.fixture(autouse=True)
def fake_thumbnails():
    """썸네일은 원본을 내려받아 줄여야 하므로 기본은 주소만 만드는 가짜로 바꾼다.
    실제 생성을 시험하는 test_thumbnails.py는 같은 이름의 fixture로 이 가짜를 끈다."""
    def fake(image_url):
        return f'/media/lite/thumbs/{hashlib.sha256(image_url.encode()).hexdigest()[:8]}.webp'

    with mock.patch('lite.thumbnails.make_thumbnail', side_effect=fake), \
            mock.patch('lite.views.admin.make_thumbnail', side_effect=fake):
        yield fake


@pytest.fixture
def make_member(db):
    def _make(name='민수', is_host=False):
        return Member.objects.create(name=name, is_host=is_host)
    return _make


@pytest.fixture
def member(make_member):
    return make_member('민수')


@pytest.fixture
def host(make_member):
    return make_member('운영자', is_host=True)


@pytest.fixture
def auth(api_client):
    """(member) -> 해당 회원 토큰이 설정된 헤더 dict."""
    def _headers(m):
        return {'HTTP_X_MEMBER_TOKEN': m.token}
    return _headers


@pytest.fixture
def make_meetup(db):
    def _make(title='독서 모임', days=1, capacity=10, **kwargs):
        return Meetup.objects.create(
            title=title, starts_at=timezone.now() + timedelta(days=days),
            location='강남', capacity=capacity, **kwargs,
        )
    return _make
