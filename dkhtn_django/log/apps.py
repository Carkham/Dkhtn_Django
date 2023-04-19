from django.apps import AppConfig


class UserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dkhtn_django.log'

    def ready(self):
        from .log_consumer import LogConsuming
        consumer = LogConsuming()
        consumer.daemon = True
        consumer.start()
