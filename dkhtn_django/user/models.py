from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.


class User(AbstractUser):
    id = models.AutoField
    username = models.CharField(max_length=16, unique=True, verbose_name='名字')
    password = models.CharField(max_length=256, verbose_name='密码')
    email = models.CharField(max_length=32, unique=True, verbose_name='邮箱')
    avatar = models.CharField(max_length=4, verbose_name='头像')
