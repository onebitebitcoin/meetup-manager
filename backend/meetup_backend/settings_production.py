"""
Production settings for meetup_backend project.
"""
import os

from .settings import *  # noqa: F403

# Override debug settings
DEBUG = False

# Update allowed hosts / site URL for production
ALLOWED_HOSTS = [host.strip() for host in os.environ.get('ALLOWED_HOSTS', 'meet.onebitebitcoin.com').split(',') if host.strip()]
SITE_URL = os.environ.get('SITE_URL', 'https://meet.onebitebitcoin.com')

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# HTTPS settings (enabled for meet.onebitebitcoin.com)
SECURE_SSL_REDIRECT = True
SECURE_REDIRECT_EXEMPT = [r'^api/health/$']
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Static files with whitenoise
MIDDLEWARE = [  # noqa: F405
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add this for static files
] + MIDDLEWARE[1:]  # noqa: F405

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Override media files path for production
MEDIA_ROOT = '/var/www/meet/media'
FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755

# Database is inherited from settings.py and uses DATABASE_URL when provided.

# Cloud storage settings (uncomment and configure for production)
# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
# AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
# AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
# AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
# AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', 'us-east-1')
# AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
# AWS_DEFAULT_ACL = None
# AWS_S3_OBJECT_PARAMETERS = {
#     'CacheControl': 'max-age=86400',
# }

# Logging
# Prefer stdout logging (12-factor). File logging is optional and enabled only when writable.
LOG_DIR = os.environ.get("DJANGO_LOG_DIR", "/var/log/meetup")
LOG_FILE = os.environ.get("DJANGO_LOG_FILE", f"{LOG_DIR}/django.log")

file_logging_enabled = False
try:
    os.makedirs(LOG_DIR, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8"):
        pass
    file_logging_enabled = True
except OSError:
    file_logging_enabled = False

log_handlers = {
    "console": {
        "level": "INFO",
        "class": "logging.StreamHandler",
        "formatter": "verbose",
    },
}
root_handlers = ["console"]

if file_logging_enabled:
    log_handlers["file"] = {
        "level": "INFO",
        "class": "logging.FileHandler",
        "filename": LOG_FILE,
        "formatter": "verbose",
    }
    root_handlers.append("file")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
    },
    "handlers": log_handlers,
    "root": {
        "handlers": root_handlers,
        "level": "INFO",
    },
}
