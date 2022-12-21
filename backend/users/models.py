from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import F, Q
from foodgram.settings import AUTH_USER_MODEL
from .managers import CustomUserManager


class User(AbstractUser):
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'
    ROLES = {
        (ADMIN, 'Админ'),
        (MODERATOR, 'Модератор'),
        (USER, 'Пользователь')
    }
    username = models.CharField(
        'Логин',
        max_length=150,
        unique=True,
        error_messages={
            'unique': 'Пользователь с таким никнеймом уже существует!',
        },
        help_text='Укажите свой никнейм.',
    )
    first_name = models.CharField(
        'Имя',
        max_length=150,
        blank=True,
        help_text='Укажите своё имя.',
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150,
        blank=True,
        help_text='Укажите свою фамилию.',
    )
    email = models.EmailField(
        'email адресс',
        max_length=254,
        unique=True,
        blank=False,
        error_messages={
            'unique': 'Пользователь с таким email уже существует!',
        },
        help_text='Укажите свой email.',
    )
    role = models.CharField(
        'статус',
        max_length=20,
        choices=ROLES,
        default=USER,
    )
    date_joined = models.DateTimeField(
        'Дата регистрации',
        auto_now_add=True,
    )
    password = models.CharField(
        'Пароль',
        max_length=150,
        help_text='Введите пароль.',
    )

    @property
    def is_moderator(self):
        return self.is_staff or self.role == self.MODERATOR

    @property
    def is_admin(self):
        return self.is_superuser or self.role == self.ADMIN

    def __str__(self):
        return self.get_full_name()

    objects = CustomUserManager()

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class ConfirmationCode(models.Model):
    user = models.OneToOneField('User', on_delete=models.CASCADE)
    token = models.CharField(max_length=255)


class Follow(models.Model):
    user = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='following'
    )

    def __str__(self):
        return f'{self.user} - {self.author}'

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_follow',
            ),
            models.CheckConstraint(
                check=~Q(user=F('author')),
                name='non_self_following',
            ),
        )
