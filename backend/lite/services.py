"""LITE 공용 도메인 헬퍼: 시간대 판단, 메시지 추가, 쿼리셋."""
from datetime import datetime, time
from zoneinfo import ZoneInfo

from django.db.models import Count, Q
from django.utils import timezone

from .models import ChatMessage, Meetup, MeetupRequest, Rsvp

KST = ZoneInfo('Asia/Seoul')


def today_kst():
    return timezone.now().astimezone(KST).date()


def today_start_kst():
    return datetime.combine(today_kst(), time.min, tzinfo=KST)


def is_today(dt):
    return dt.astimezone(KST).date() == today_kst()


def add_message(room, body, kind=ChatMessage.Kind.SYSTEM, member=None):
    return ChatMessage.objects.create(room=room, member=member, kind=kind, body=body)


def meetups_with_counts():
    return Meetup.objects.select_related('room').annotate(
        going_count=Count('rsvps', filter=Q(rsvps__status=Rsvp.Status.GOING)),
        maybe_count=Count('rsvps', filter=Q(rsvps__status=Rsvp.Status.MAYBE)),
    )


def requests_with_votes():
    return MeetupRequest.objects.select_related('created_by').annotate(vote_count=Count('votes'))
