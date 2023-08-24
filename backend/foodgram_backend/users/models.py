import datetime as dt
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
#from api_yamdb.settings import DEFAULT_LENGTH, LENGTH_USERNAME
from django.core.exceptions import ValidationError


def validate_username_me(value):
    if value.lower() == 'me':
        raise ValidationError(
            'Имя пользователя не может быть "me".'
        )


class User(AbstractUser):
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'
    ROLES = [
        (ADMIN, 'Administrator'),
        (MODERATOR, 'Moderator'),
        (USER, 'User'),
    ]
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    username_validator = UnicodeUsernameValidator()

    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        unique=True,
    )
    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=100,   #LENGTH_USERNAME,
        unique=True,
        validators=[
            username_validator,
            validate_username_me
        ]
    )
    role = models.CharField(
        verbose_name='Роль',
        max_length=50,
        choices=ROLES,
        default=USER
    )
    bio = models.TextField(
        verbose_name='О себе',
        null=False,
        blank=True
    )

    class Meta:
        ordering = ['username']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

        constraints = [
            models.CheckConstraint(
                check=~models.Q(username__iexact='me'),
                name='username_is_not_me'
            ),
        ]

    def __str__(self):
        return self.username

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser