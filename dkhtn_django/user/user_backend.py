from django.contrib.auth.backends import ModelBackend, UserModel
from . import models


class UserBackend(ModelBackend):
    """
    令原authenticate支持邮箱+密码验证.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = models.User.objects.get(username=username)
            user.check_password(password)
            return user
        except UserModel.DoesNotExist:
            try:
                user = models.User.objects.get(email=username)
                user.check_password(password)
                return user
            except UserModel.DoesNotExist:
                return None
