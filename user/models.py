from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.


class User(AbstractUser):
    id = models.AutoField
    username = models.CharField(max_length=16, unique=True, verbose_name='名字')
    password = models.CharField(max_length=256, verbose_name='密码')
    mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号')
