from django.urls import path
import dkhtn_django.user.views as user_views

urlpatterns = [
    # user urls

    # email
    path("email-send", user_views.email_send, name="email-send"),
    path("email-check", user_views.email_check),
]
