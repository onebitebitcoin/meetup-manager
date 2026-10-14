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


def test_import_copies_external_image_url(db):
    old = _legacy('이미지', 3)
    Legacy.objects.filter(pk=old.pk).update(image_url='https://example.com/a.png')
    run()
    assert LiteMeetup.objects.get().image_url == 'https://example.com/a.png'


def test_import_copies_uploaded_image_as_media_path(db):
    old = _legacy('업로드', 3)
    Legacy.objects.filter(pk=old.pk).update(image='meetups/b.png')
    run()
    assert LiteMeetup.objects.get().image_url.endswith('/meetups/b.png')


def test_reimport_fills_missing_thumbnail_but_keeps_existing_one(db):
    old = _legacy('나중 이미지', 3)
    run()
    assert LiteMeetup.objects.get().image_url == ''
    Legacy.objects.filter(pk=old.pk).update(image_url='https://example.com/new.png')

    out = run()

    assert LiteMeetup.objects.get().image_url == 'https://example.com/new.png'
    assert '썸네일 채움 1개' in out
    Legacy.objects.filter(pk=old.pk).update(image_url='https://example.com/other.png')
    run()
    assert LiteMeetup.objects.get().image_url == 'https://example.com/new.png'
