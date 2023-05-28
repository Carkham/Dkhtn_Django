from django.contrib.auth.backends import ModelBackend, UserModel
from . import models


def check_username(username, password):
    try:
        user = models.User.objects.get(username=username)
        if user.check_password(password):
            return user
        else:
            return None
    except UserModel.DoesNotExist:
        return None


def check_email(email, password):
    try:
        user = models.User.objects.get(email=email)
        if user.check_password(password):
            return user
        else:
            return None
    except UserModel.DoesNotExist:
        return None


class UserBackend(ModelBackend):
    """
    令原authenticate支持邮箱+密码验证.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = check_username(username, password)
        if user is None:
            user = check_email(username, password)
        return user
