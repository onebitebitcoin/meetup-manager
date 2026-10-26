from django.core.management.base import BaseCommand

from lite.thumbnails import fill_missing_thumbnails


class Command(BaseCommand):
    help = '원본 이미지 주소는 있는데 썸네일이 없는 LITE 모임의 썸네일(WebP)을 만든다. 여러 번 실행해도 안전하다.'

    def handle(self, *args, **options):
        made, failed = fill_missing_thumbnails()
        for meetup_id, reason in failed:
            self.stdout.write(self.style.WARNING(f'모임 {meetup_id}: {reason}'))
        self.stdout.write(self.style.SUCCESS(f'썸네일 만듦 {made}개, 실패 {len(failed)}개'))
