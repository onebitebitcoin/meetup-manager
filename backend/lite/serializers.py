"""LITE 응답 객체 직렬화 함수. 계약은 SPEC.md 11.4 공통 객체를 따른다."""
from .models import ChatMessage, RequestVote, Rsvp
from .services import is_today


def member_brief(member):
    return {'id': member.id, 'name': member.name}


def member_full(member):
    return {'id': member.id, 'name': member.name, 'is_host': member.is_host}


def meetup_card(meetup, my_status=None):
    """meetup은 meetups_with_counts()로 조회한 객체(going_count/maybe_count annotate 필요)."""
    return {
        'id': meetup.id,
        'title': meetup.title,
        'starts_at': meetup.starts_at.isoformat(),
        'location': meetup.location,
        'capacity': meetup.capacity,
        'going_count': meetup.going_count,
        'maybe_count': meetup.maybe_count,
        'my_status': my_status,
        'from_request': meetup.from_request_id is not None,
        'is_today': is_today(meetup.starts_at),
        'room_id': meetup.room.id,
    }


def my_statuses(member, meetup_ids):
    return dict(
        Rsvp.objects.filter(member=member, meetup_id__in=meetup_ids).values_list('meetup_id', 'status')
    )


def message_obj(message):
    return {
        'id': message.id,
        'kind': message.kind,
        'member': member_brief(message.member) if message.member else None,
        'body': message.body,
        'created_at': message.created_at.isoformat(),
    }


def seminar_card(seminar):
    last = ChatMessage.objects.filter(room=seminar.room).order_by('-id').values_list('body', flat=True).first()
    return {
        'id': seminar.id,
        'member': member_brief(seminar.member),
        'mode': seminar.mode,
        'status': seminar.status,
        'room_id': seminar.room.id,
        'last_message': last,
    }


def request_card(req, member, threshold):
    """req는 requests_with_votes()로 조회한 객체(vote_count annotate 필요)."""
    return {
        'id': req.id,
        'title': req.title,
        'preferred_period': req.preferred_period,
        'created_by': member_brief(req.created_by),
        'vote_count': req.vote_count,
        'voted': RequestVote.objects.filter(request=req, member=member).exists(),
        'status': req.status,
        'meetup_id': req.meetup_id,
        'threshold': threshold,
    }
