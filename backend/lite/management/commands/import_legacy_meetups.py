from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from lite.models import ChatRoom
from lite.models import Meetup as LiteMeetup
from meetups.models import Meetup as LegacyMeetup


class Command(BaseCommand):
    help = '기존 meetups.Meetup을 lite.Meetup으로 복사한다. 이미 복사된 모임은 건너뛴다.'

    def add_arguments(self, parser):
        parser.add_argument('--all', action='store_true', help='지난 모임까지 모두 복사')

    def handle(self, *args, **options):
        legacy = LegacyMeetup.objects.order_by('id')
        if not options['all']:
            legacy = legacy.filter(date_time__gte=timezone.now())
        existing = set(
            LiteMeetup.objects.filter(legacy_meetup_id__isnull=False).values_list('legacy_meetup_id', flat=True)
        )
        created = skipped = 0
        for old in legacy:
            if old.id in existing:
                skipped += 1
                continue
            with transaction.atomic():
                meetup = LiteMeetup.objects.create(
                    title=old.name[:80],
                    description=old.description or '',
                    starts_at=old.date_time,
                    location=old.location[:100],
                    capacity=max(old.max_participants, 1),
                    legacy_meetup_id=old.id,
                )
                ChatRoom.objects.create(kind=ChatRoom.Kind.MEETUP, meetup=meetup)
            created += 1
        self.stdout.write(self.style.SUCCESS(f'가져온 모임 {created}개, 건너뜀 {skipped}개'))
