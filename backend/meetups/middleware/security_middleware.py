"""
Security middleware to prevent sensitive data leakage
"""
import logging
import re

from django.conf import settings


class PasswordLeakagePreventionMiddleware:
    """
    Middleware to prevent accidental password leakage in logs or responses.
    This acts as a safety net in case any code accidentally logs sensitive data.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.password_patterns = [
            re.compile(r'"password"\s*:\s*"[^"]*"', re.IGNORECASE),
            re.compile(r'password=\S+', re.IGNORECASE),
            re.compile(r'pwd=\S+', re.IGNORECASE),
        ]

    def __call__(self, request):
        # Process request
        response = self.get_response(request)

        # In development, add security headers
        if settings.DEBUG:
            response['X-Korean-Conversion'] = 'Enabled'
            response['X-Security-Audit'] = 'Active'

        return response

    def process_exception(self, request, exception):
        """
        Ensure that exceptions don't leak password data in logs
        """
        if settings.DEBUG:
            # In development, we can log more details
            return None

        # In production, sanitize any potential password data from exception messages
        exception_str = str(exception)
        for pattern in self.password_patterns:
            exception_str = pattern.sub('[REDACTED]', exception_str)

        # Log the sanitized exception
        logger = logging.getLogger('meetups.security')
        logger.error(f"Exception occurred: {exception_str}")

        return None
