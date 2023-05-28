from django.urls import path
import dkhtn_django.user.views as user_views

urlpatterns = [
    # user urls
    path("rsa-pub", user_views.rsa_get),
    path("login", user_views.login),
    path("register", user_views.register),
    path("info", user_views.userinfo_get),
    path("uname-change", user_views.username_change),
    path("password-change", user_views.password_change),
    path("email-change", user_views.email_change),
    path("avatar-change", user_views.avatar_change),

    # email
    path("email-send", user_views.email_send),
    path("email-check", user_views.email_check),
]
