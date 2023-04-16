from django.apps import AppConfig
from django.conf import settings


class UserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user'

    def ready(self):
        from .rabbit.EmailSender import start_email_sender
        if not settings.DEBUG:
            start_email_sender()
