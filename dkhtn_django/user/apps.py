from django.apps import AppConfig
from .rabbit.EmailSender import AMQPConsuming


class UserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dkhtn_django.user'

    def ready(self):
        consumer = AMQPConsuming()
        consumer.daemon = True
        consumer.start()
