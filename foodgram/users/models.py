from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

username_validator = RegexValidator(
    regex=r'^[\w.@+-]+\Z',
    message='Значение поля username не соответствует регулярному выражению ^[\w.@+-]+\Z'
)

class User(AbstractUser):
    email = models.EmailField(
        blank=False,
        unique=True,
        max_length=254,
        verbose_name='мейл',
        help_text='Добавьте имейл'
    )
    username = models.CharField(
        blank=False,
        unique=True,
        max_length=150,
        verbose_name='Юзернейм',
        help_text='Добавьте юзернейм',
        validators=[username_validator]
    )
    first_name = models.CharField(
        blank=False,
        max_length=150,
        verbose_name='имя',
        help_text='Введите имя'
    )
    last_name = models.CharField(
        blank=False,
        max_length=150,
        verbose_name='Фаиилия',
        help_text='Введите фамилию'
    )
    password = models.CharField(
        blank=False,
        max_length=150,
        verbose_name='Пароль',
        help_text='Введите пароль'
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'password']

    class Meta:
        ordering = ['username']

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    

class Subscribe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipe_author',
        verbose_name='Автор'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='current_user',
        verbose_name='Залогиненный пользователь'
    )

    class Meta:
        ordering = ['user']

    def __str__(self):
        return f'{self.author}, {self.user}'