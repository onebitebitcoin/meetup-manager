from datetime import timedelta
from io import StringIO

from django.core.management import call_command
from django.utils import timezone

from lite.models import ChatRoom
from lite.models import Meetup as LiteMeetup
from meetups.models import Meetup as Legacy


def _legacy(name, days):
    return Legacy.objects.create(
        name=name, description='d', date_time=timezone.now() + timedelta(days=days),
        location='서울', max_participants=12,
    )


def run(*args):
    out = StringIO()
    call_command('import_legacy_meetups', *args, stdout=out)
    return out.getvalue()


def test_import_future_only_and_idempotent(db):
    future = _legacy('미래', 3)
    _legacy('과거', -3)
    run()
    assert LiteMeetup.objects.count() == 1
    m = LiteMeetup.objects.get()
    assert (m.title, m.capacity, m.location, m.legacy_meetup_id) == ('미래', 12, '서울', future.id)
    assert ChatRoom.objects.filter(meetup=m).exists()
    out = run()
    assert LiteMeetup.objects.count() == 1 and ChatRoom.objects.count() == 1
    assert '가져온 모임 0개' in out


def test_import_all(db):
    _legacy('미래', 3)
    _legacy('과거', -3)
    run('--all')
    assert LiteMeetup.objects.count() == 2
    run('--all')
    assert LiteMeetup.objects.count() == 2
