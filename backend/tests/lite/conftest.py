from datetime import timedelta

import pytest
from django.core.cache import cache
from django.utils import timezone

from lite.models import ChatRoom, Meetup, Member


@pytest.fixture(autouse=True)
def clear_throttle_cache():
    cache.clear()
    yield
    cache.clear()


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
        meetup = Meetup.objects.create(
            title=title, starts_at=timezone.now() + timedelta(days=days),
            location='강남', capacity=capacity, **kwargs,
        )
        ChatRoom.objects.create(kind=ChatRoom.Kind.MEETUP, meetup=meetup)
        return meetup
    return _make
