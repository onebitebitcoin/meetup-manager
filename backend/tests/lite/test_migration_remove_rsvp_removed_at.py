from datetime import timedelta

import pytest
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.utils import timezone

BEFORE = [('lite', '0014_liteconfig_admin_password_hash')]
AFTER = [('lite', '0015_remove_rsvp_removed_at')]


def migrate_to(target):
    executor = MigrationExecutor(connection)
    executor.loader.build_graph()
    executor.migrate(target)
    return executor.loader.project_state(target).apps


@pytest.mark.django_db(transaction=True)
def test_removed_rsvps_are_deleted_and_others_kept():
    apps = migrate_to(BEFORE)
    Member = apps.get_model('lite', 'Member')
    Meetup = apps.get_model('lite', 'Meetup')
    Rsvp = apps.get_model('lite', 'Rsvp')
    meetup = Meetup.objects.create(
        title='거래소 탈출', starts_at=timezone.now() + timedelta(days=1), location='카페', capacity=10,
    )
    kicked = Member.objects.create(name='해맑은 오리', token='t1')
    staying = Member.objects.create(name='명랑한 달팽이', token='t2')
    Rsvp.objects.create(member=kicked, meetup=meetup, status='no', removed_at=timezone.now())
    Rsvp.objects.create(member=staying, meetup=meetup, status='going')

    apps = migrate_to(AFTER)

    Rsvp = apps.get_model('lite', 'Rsvp')
    assert list(Rsvp.objects.values_list('member__name', 'status')) == [('명랑한 달팽이', 'going')]
