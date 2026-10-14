"""LITE 요청 횟수 제한. 카운터는 Django 캐시(FileBasedCache)에 저장해 워커 간에 공유한다."""
from rest_framework.throttling import AnonRateThrottle, SimpleRateThrottle


class MemberCreateThrottle(AnonRateThrottle):
    scope = 'lite_member_create'
    rate = '60/hour'


class MemberThrottle(SimpleRateThrottle):
    """회원 단위 제한. methods가 지정되면 해당 HTTP 메서드만 센다."""

    methods = None

    def allow_request(self, request, view):
        if self.methods and request.method not in self.methods:
            return True
        return super().allow_request(request, view)

    def get_cache_key(self, request, view):
        return self.cache_format % {'scope': self.scope, 'ident': self.get_ident_for(request, view)}

    def get_ident_for(self, request, view):
        return str(request.auth.pk)


class HostClaimThrottle(MemberThrottle):
    scope = 'lite_host_claim'
    rate = '5/hour'

    def get_ident_for(self, request, view):
        return f'{request.auth.pk}_{self.get_ident(request)}'


class CheckinThrottle(MemberThrottle):
    """도착 코드 대입 방어: 회원·모임 기준, 성공과 실패 모두 센다."""

    scope = 'lite_checkin'
    rate = '5/10min'

    def parse_rate(self, rate):
        # DRF는 'N/단위'만 지원하므로 10분 창은 직접 지정한다
        return 5, 600

    def get_ident_for(self, request, view):
        return f'{request.auth.pk}_{view.kwargs["meetup_id"]}'


class MessageSendThrottle(MemberThrottle):
    scope = 'lite_message_send'
    rate = '30/min'
    methods = ('POST',)


class RequestCreateThrottle(MemberThrottle):
    scope = 'lite_request_create'
    rate = '10/hour'
    methods = ('POST',)


class SeminarModeThrottle(MemberThrottle):
    scope = 'lite_seminar_mode'
    rate = '10/hour'
