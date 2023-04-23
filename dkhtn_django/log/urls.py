from django.urls import path

from .views import query_log

urlpatterns = [
    path("<str:func_id>", query_log)
]
