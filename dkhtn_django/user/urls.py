from django.urls import path
import dkhtn_django.user.views as user_views

urlpatterns = [
    # user urls
    path("rsa-pub", user_views.rsa_get),
    path("login", user_views.login),

    # email
    path("email-send", user_views.email_send),
    path("email-check", user_views.email_check),
]
