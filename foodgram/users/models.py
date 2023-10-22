from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import AbstractUser

username_validator = RegexValidator(
    message='Значение поля username не соответствует регулярному выражен'
)


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
        verbose_name='пользователь',
        validators=[username_validator]
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
    REQUIRED_FIELDS = ['username', 'password']


class Subscribe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipe_author'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='current_user'
    )
