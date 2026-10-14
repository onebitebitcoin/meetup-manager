from django.apps import AppConfig


class LiteConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'lite'

    def ready(self):
        from . import signals  # noqa: F401
