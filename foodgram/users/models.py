from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(
        blank=False,
        unique=True,
        max_length=254,
        verbose_name='мейл'
    )
    username = models.CharField(
        blank=False,
        unique=True,
        max_length=150,
        verbose_name='пользователь'
    )
    first_name = models.CharField(
        blank=False,
        max_length=150,
        verbose_name='имя'
    )
    last_name = models.CharField(
        blank=False,
        max_length=150,
        verbose_name='фаиилия'
    )
    password = models.CharField(
        blank=False,
        max_length=150
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ["username", "password"]