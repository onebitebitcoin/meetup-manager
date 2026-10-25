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


class LinkPreviewThrottle(MemberThrottle):
    scope = 'lite_link_preview'
    rate = '60/min'
