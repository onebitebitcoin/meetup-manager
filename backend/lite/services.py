"""LITE 공용 도메인 헬퍼: 시간대 판단, 메시지 추가, 쿼리셋."""
from datetime import datetime, time
from zoneinfo import ZoneInfo

from django.db import IntegrityError, transaction
from django.db.models import Count, OuterRef, Q, Subquery
from django.utils import timezone

from .models import ChatMessage, Meetup, MeetupRequest, RoomRead, Rsvp, SeminarRequest

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


def seminars_with_last_message():
    last_body = ChatMessage.objects.filter(room__seminar=OuterRef('pk')).order_by('-id').values('body')[:1]
    return SeminarRequest.objects.select_related('member', 'room').annotate(last_message=Subquery(last_body))


def mark_read(member, room, last_id):
    """member가 room에서 last_id까지 읽었다고 기록한다. 이미 더 뒤까지 읽었으면 그대로 둔다."""
    # 폴링마다 불리므로 흔한 경우(기록이 이미 있음)는 UPDATE 한 번으로 끝낸다
    if RoomRead.objects.filter(member=member, room=room, last_read_id__lt=last_id).update(last_read_id=last_id):
        return
    if not RoomRead.objects.filter(member=member, room=room).exists():
        try:
            with transaction.atomic():
                RoomRead.objects.create(member=member, room=room, last_read_id=last_id)
        except IntegrityError:
            mark_read(member, room, last_id)  # 동시에 다른 요청이 먼저 만든 경우


def unread_count(member, room):
    """member가 아직 읽지 않은 대화 수. 사람이 쓴 메시지만 세고 내가 쓴 것과 시스템·안내 문구는 뺀다."""
    last_read = RoomRead.objects.filter(member=member, room=room).values_list('last_read_id', flat=True).first() or 0
    return (
        ChatMessage.objects.filter(room=room, kind=ChatMessage.Kind.USER, id__gt=last_read)
        .exclude(member=member)
        .count()
    )
