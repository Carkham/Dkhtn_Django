from django.urls import path
from .views import resource_query

urlpatterns = [
    path("query-resource", resource_query)
]
