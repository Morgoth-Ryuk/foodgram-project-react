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
    #ADMIN = 'admin'
    #MODERATOR = 'moderator'
    #USER = 'user'
    #ROLES = [
        #(ADMIN, 'Administrator'),
        #(MODERATOR, 'Moderator'),
        #(USER, 'User'),
    #]
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    username_validator = UnicodeUsernameValidator()

    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=100, #MAX_LEN_EMAIL_FIELD
        unique=True,
        help_text='Введите адрес электронной почты'
    )
    username = models.CharField(
        verbose_name='Никнэйм пользователя',
        max_length=100,   #LENGTH_USERNAME,
        unique=True,
        validators=[
            username_validator,
            validate_username_me #добавить валидацию мин длины?
        ]
    )
    first_name = models.CharField(
        verbose_name='Имя пользователя',
        max_length=100,
        help_text='Введите Ваше имя',
        # validators=
        ),
    last_name = models.CharField(
        verbose_name='Фамилия пользователя',
        max_length=100,
        help_text='Введите Вашу Фамилию',
        #validators=
        ),

    password = models.CharField(
        verbose_name='Пароль',   #_('Пароль'),
        max_length=128,
        help_text='Введите пароль',
    )
    is_subscribed = models.BooleanField(
        verbose_name='Подписан',
        default=False,
    )
    #role = models.CharField(
        #verbose_name='Роль',
        #max_length=50,
        #choices=ROLES,
        #default=USER
    #)

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


    #@property
    #def is_moderator(self):
        #return self.role == self.MODERATOR

    #@property
    #def is_admin(self):
        #return self.role == self.ADMIN or self.is_superuser


class Subscriptions(models.Model):
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
                name='\nRepeat subscription\n',
                #name='unique_follow'
            ),
            models.CheckConstraint(
                check=~models.Q(author=models.F('user')), name='\nNo self sibscription\n'
            ),
        )

    def __str__(self) -> str:
        return f'{self.user.username} -> {self.author.username}'
    #def __str__(self):
        #return '{user}, {author}'.format(
            #author=self.author.username,
           # user=self.user.username
        #)
