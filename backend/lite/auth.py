from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from rest_framework.permissions import BasePermission

from .models import Member

TOKEN_HEADER = 'HTTP_X_MEMBER_TOKEN'
UNAUTHORIZED_MESSAGE = '이름을 먼저 입력해 주세요'
HOST_ONLY_MESSAGE = '운영자만 할 수 있어요'


class MemberTokenAuthentication(BaseAuthentication):
    """X-Member-Token 헤더로 Member를 찾아 request.member / request.auth에 채운다."""

    def authenticate(self, request):
        token = request.META.get(TOKEN_HEADER, '').strip()
        if not token:
            return None
        member = Member.objects.filter(token=token).first()
        if member is None:
            raise AuthenticationFailed(UNAUTHORIZED_MESSAGE)
        request.member = member
        return (None, member)

    def authenticate_header(self, request):
        return 'X-Member-Token'


class IsMember(BasePermission):
    message = UNAUTHORIZED_MESSAGE

    def has_permission(self, request, view):
        return isinstance(request.auth, Member)


class IsHost(BasePermission):
    message = HOST_ONLY_MESSAGE

    def has_permission(self, request, view):
        if not isinstance(request.auth, Member):
            raise AuthenticationFailed(UNAUTHORIZED_MESSAGE)
        if not request.auth.is_host:
            raise PermissionDenied(HOST_ONLY_MESSAGE)
        return True
