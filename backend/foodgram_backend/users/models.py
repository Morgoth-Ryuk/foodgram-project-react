from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError


def validate_username_me(value):
    if value.lower() == 'me':
        raise ValidationError(
            'Имя пользователя не может быть "me".'
        )


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    username_validator = UnicodeUsernameValidator()

    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=100,
        unique=True,
        help_text='Введите адрес электронной почты'
    )
    username = models.CharField(
        verbose_name='Никнэйм пользователя',
        max_length=20,
        unique=True,
        validators=[
            username_validator,
            validate_username_me
        ]
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=20
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=20
    )

    password = models.CharField(
        verbose_name='Пароль',   # _('Пароль'),
        max_length=128,
        help_text='Введите пароль',
    )
    is_subscribed = models.BooleanField(
        verbose_name='Подписан',
        default=False,
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

    def __str__(self) -> str:
        return f'{self.username}: {self.email}'



class Subscription(models.Model):
    """
    Подписки пользователей друг на друга.
    """

    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        related_name='subscribers',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        verbose_name='Подписчики',
        related_name='subscriptions',
        on_delete=models.CASCADE,
    )
    date_added = models.DateTimeField(
        verbose_name='Дата создания подписки',
        auto_now_add=True,
        editable=False,
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('author', 'user'),
                name='unique_follow',
            ),
            models.CheckConstraint(
                check=~models.Q(
                    author=models.F('user')
                ), name='self sibscription'
            ),
        )

    def __str__(self) -> str:
        return f'{self.user.username} -> {self.author.username}'
