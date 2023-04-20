from django.apps import AppConfig


class MonitorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dkhtn_django.monitor'

    def ready(self):
        from .resource import MonitorConsuming
        monitor = MonitorConsuming()
        monitor.start()
