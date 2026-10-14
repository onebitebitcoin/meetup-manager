from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from lite.models import Meetup as LiteMeetup
from meetups.models import Meetup as LegacyMeetup


def legacy_image_url(old):
    """업로드 이미지가 있으면 /media/ 경로를, 없으면 외부 image_url을 쓴다."""
    if old.image:
        return old.image.url[:500]
    return (old.image_url or '')[:500]


class Command(BaseCommand):
    help = (
        '기존 meetups.Meetup을 lite.Meetup으로 복사한다. 이미 복사된 모임은 다시 만들지 않고, '
        '썸네일이 비어 있을 때만 기존 이미지로 채운다.'
    )

    def add_arguments(self, parser):
        parser.add_argument('--all', action='store_true', help='지난 모임까지 모두 복사')

    def handle(self, *args, **options):
        legacy = LegacyMeetup.objects.order_by('id')
        if not options['all']:
            legacy = legacy.filter(date_time__gte=timezone.now())
        existing = {
            m.legacy_meetup_id: m for m in LiteMeetup.objects.filter(legacy_meetup_id__isnull=False)
        }
        created = skipped = image_filled = 0
        for old in legacy:
            current = existing.get(old.id)
            if current is not None:
                image = legacy_image_url(old)
                if image and not current.image_url:
                    LiteMeetup.objects.filter(pk=current.pk).update(image_url=image)
                    image_filled += 1
                skipped += 1
                continue
            with transaction.atomic():
                LiteMeetup.objects.create(
                    title=old.name[:80],
                    description=old.description or '',
                    starts_at=old.date_time,
                    location=old.location[:100],
                    capacity=max(old.max_participants, 1),
                    image_url=legacy_image_url(old),
                    legacy_meetup_id=old.id,
                )
            created += 1
        self.stdout.write(self.style.SUCCESS(f'가져온 모임 {created}개, 건너뜀 {skipped}개, 썸네일 채움 {image_filled}개'))
