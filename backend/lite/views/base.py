import logging

from django.db.utils import DataError
from rest_framework import status
from rest_framework.exceptions import APIException, NotAuthenticated, Throttled
from rest_framework.views import APIView

from ..auth import UNAUTHORIZED_MESSAGE, IsMember, MemberTokenAuthentication

logger = logging.getLogger(__name__)


class ApiError(APIException):
    """`{"error": message}` 형식으로 응답되는 예외."""

    def __init__(self, message, status_code=status.HTTP_400_BAD_REQUEST):
        self.status_code = status_code
        super().__init__(message)


def not_found(message='찾을 수 없어요'):
    return ApiError(message, status.HTTP_404_NOT_FOUND)


def get_or_404(queryset, message='찾을 수 없어요', **kwargs):
    try:
        obj = queryset.filter(**kwargs).first()
    except (OverflowError, DataError):
        raise not_found(message) from None
    if obj is None:
        raise not_found(message)
    return obj


class LiteView(APIView):
    authentication_classes = [MemberTokenAuthentication]
    permission_classes = [IsMember]

    @property
    def member(self):
        return self.request.auth

    def handle_exception(self, exc):
        response = super().handle_exception(exc)
        if isinstance(exc, Throttled):
            response.data = {'error': '잠시 후 다시 시도해 주세요'}
        elif isinstance(exc, NotAuthenticated):
            response.data = {'error': UNAUTHORIZED_MESSAGE}
        elif isinstance(exc, APIException):
            detail = exc.detail
            response.data = {'error': detail if isinstance(detail, str) else '잘못된 요청이에요'}
        elif response.status_code == status.HTTP_404_NOT_FOUND:
            response.data = {'error': '찾을 수 없어요'}
        return response

    def json_body(self):
        data = self.request.data
        return data if hasattr(data, 'get') else {}


def clean_text(value, label, min_len, max_len):
    """문자열 필드를 strip 후 길이 검증한다."""
    if not isinstance(value, str):
        raise ApiError(f'{label}을(를) 입력해 주세요')
    value = value.strip()
    if len(value) < min_len:
        raise ApiError(f'{label}을(를) 입력해 주세요')
    if len(value) > max_len:
        raise ApiError(f'{label}은(는) {max_len}자 이내로 입력해 주세요')
    return value
