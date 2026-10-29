import logging

from django.db import transaction

from meetups.views.helpers import APIResponse

from ..auth import IsMember, IsOpenOrHost
from ..models import LiteConfig, MeetupRequest, RequestVote
from ..serializers import request_card, voted_request_ids
from ..services import requests_with_votes
from ..throttles import RequestCreateThrottle
from .base import ApiError, LiteView, clean_text, get_or_404

logger = logging.getLogger(__name__)


class RequestListView(LiteView):
    permission_classes = [IsMember, IsOpenOrHost]
    throttle_classes = [RequestCreateThrottle]

    def get(self, request):
        member = self.member
        threshold = LiteConfig.get().vote_threshold
        reqs = sorted(
            requests_with_votes(),
            key=lambda r: (r.status != MeetupRequest.Status.OPEN, -r.vote_count, -r.id),
        )
        voted_ids = voted_request_ids(member)
        return APIResponse.success({'requests': [request_card(r, voted_ids, threshold) for r in reqs]})

    def post(self, request):
        member = self.member
        data = self.json_body()
        title = clean_text(data.get('title'), '제목', 1, 60)
        period = data.get('preferred_period')
        if period not in MeetupRequest.Period.values:
            raise ApiError('희망 시기는 this_month, next_month, any 중 하나여야 해요')
        with transaction.atomic():
            req = MeetupRequest.objects.create(title=title, preferred_period=period, created_by=member)
            RequestVote.objects.create(request=req, member=member)
        logger.info('LITE 모임 요청 생성: id=%s', req.id)
        card = request_card(requests_with_votes().get(pk=req.pk), {req.pk}, LiteConfig.get().vote_threshold)
        return APIResponse.created({'request': card})


class RequestVoteView(LiteView):
    permission_classes = [IsMember, IsOpenOrHost]
    def post(self, request, request_id):
        member = self.member
        with transaction.atomic():
            req = get_or_404(MeetupRequest.objects.select_for_update(), '요청을 찾을 수 없어요', pk=request_id)
            if req.status != MeetupRequest.Status.OPEN:
                raise ApiError('이미 모임이 열린 요청이에요')
            deleted, _ = RequestVote.objects.filter(request=req, member=member).delete()
            if not deleted:
                RequestVote.objects.create(request=req, member=member)
        voted_ids = set() if deleted else {req.pk}
        card = request_card(requests_with_votes().get(pk=req.pk), voted_ids, LiteConfig.get().vote_threshold)
        return APIResponse.success({'request': card})
