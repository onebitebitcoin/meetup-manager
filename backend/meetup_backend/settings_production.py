"""
Production settings for meetup_backend project.
Nginx 리버스 프록시 환경(Ubuntu 서버)에 최적화된 설정.
"""
import os

from .settings import *  # noqa: F403

DEBUG = False

# ALLOWED_HOSTS: env-var로 제어, 기본값은 운영 도메인
ALLOWED_HOSTS = [host.strip() for host in os.environ.get('ALLOWED_HOSTS', 'meet.onebitebitcoin.com').split(',') if host.strip()]  # noqa: F405

# SITE_URL: env-var 우선, 기본값은 운영 도메인
SITE_URL = os.environ.get('SITE_URL', 'https://meet.onebitebitcoin.com')

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Nginx가 HTTPS를 처리하므로 Django의 직접 redirect 금지 (무한 루프 방지)
SECURE_SSL_REDIRECT = False
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
SECURE_HSTS_SECONDS = 3600
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# CSRF trusted origins
CSRF_TRUSTED_ORIGINS = [  # noqa: F405
    'https://meet.onebitebitcoin.com',
]

# WhiteNoise for static files (SecurityMiddleware 바로 다음에 위치)
MIDDLEWARE = [  # noqa: F405
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
] + MIDDLEWARE[2:]  # noqa: F405

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# 미디어 파일: env 없으면 /data/media (Docker volume 경로)
MEDIA_ROOT = os.environ.get('MEDIA_ROOT', '/data/media')
FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755

# Database: settings.py의 DATABASE_URL 로직이 그대로 적용됨 (별도 설정 불필요)

# Cloud storage (미디어 파일을 S3/R2에 저장할 경우 주석 해제)
# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
# AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
# AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
# AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
# AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', 'ap-northeast-2')

# Logging: 12-Factor App 원칙 - stdout만 사용
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "meetups": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
