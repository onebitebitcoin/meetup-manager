"""LITE 응답 객체 직렬화 함수. 계약은 SPEC.md 11.4 공통 객체를 따른다."""
from django.core.exceptions import ObjectDoesNotExist

from .models import RequestVote, Rsvp
from .services import is_today


def room_id_of(obj):
    """Meetup/SeminarRequest의 채팅방 id. 방이 없으면 500 대신 None을 돌려준다."""
    try:
        return obj.room.id
    except ObjectDoesNotExist:
        return None


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
        'image_url': meetup.image_url or None,
        'going_count': meetup.going_count,
        'maybe_count': meetup.maybe_count,
        'my_status': my_status,
        'from_request': meetup.from_request_id is not None,
        'is_today': is_today(meetup.starts_at),
        'cancelled': meetup.cancelled_at is not None,
        'room_id': room_id_of(meetup),
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
    """seminar는 services.seminars_with_last_message()로 조회한 객체(last_message annotate 필요)."""
    return {
        'id': seminar.id,
        'member': member_brief(seminar.member),
        'mode': seminar.mode,
        'status': seminar.status,
        'room_id': room_id_of(seminar),
        'last_message': seminar.last_message,
    }


def voted_request_ids(member):
    return set(RequestVote.objects.filter(member=member).values_list('request_id', flat=True))


def request_card(req, voted_ids, threshold):
    """req는 requests_with_votes()로 조회한 객체(vote_count annotate 필요), voted_ids는 내가 투표한 요청 id 집합."""
    return {
        'id': req.id,
        'title': req.title,
        'preferred_period': req.preferred_period,
        'created_by': member_brief(req.created_by),
        'vote_count': req.vote_count,
        'voted': req.id in voted_ids,
        'status': req.status,
        'meetup_id': req.meetup_id,
        'threshold': threshold,
    }
