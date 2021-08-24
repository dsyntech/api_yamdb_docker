import datetime as dt

from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


ROLE_USER = 'user'
ROLE_MODERATOR = 'moderator'
ROLE_ADMIN = 'admin'

ROLES = (
    (ROLE_USER, 'Пользователь'),
    (ROLE_MODERATOR, 'Модератор'),
    (ROLE_ADMIN, 'Админ')
)


class User(AbstractUser):
    email = models.EmailField(
        'Почта',
        max_length=60,
        unique=True,
        blank=False
    )
    username = models.CharField(
        'Ник пользователя',
        max_length=20,
        unique=True,
        blank=False
    )
    first_name = models.CharField(
        'Имя',
        max_length=25,
        blank=True
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=25,
        blank=True
    )
    bio = models.TextField(
        'Биография',
        blank=True
    )
    role = models.CharField(
        'Роль',
        max_length=10,
        choices=ROLES,
        default=ROLE_USER
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = (
            'username',
        )


class Category(models.Model):
    name = models.CharField(
        'Название',
        max_length=255,
    )
    slug = models.SlugField(
        unique=True,
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = (
            'slug',
        )


class Genre(models.Model):
    name = models.CharField(
        'Название',
        max_length=255,
    )
    slug = models.SlugField(
        unique=True,
    )

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = (
            'slug',
        )


class Title(models.Model):
    name = models.CharField(
        'Название',
        max_length=255,
    )
    year = models.PositiveSmallIntegerField(
        'Год',
        validators=[
            MaxValueValidator(dt.datetime.now().year,
                              'Год не может быть больше текущего')
        ]
    )
    description = models.TextField(
        'Описание',
        blank=True,
        default=''
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        blank=True,
        verbose_name='Жанр',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        blank=True,
        null=True,
        verbose_name='Категория',
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = (
            'name',
        )


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Объект обзора',
    )
    text = models.TextField('Текст')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор',
    )
    score = models.PositiveSmallIntegerField(
        'Оценка',
        validators=[
            MinValueValidator(1, 'Рейтинг не может быть меньше минимального'),
            MaxValueValidator(10, 'Превышен максимально допустимый рейтинг'),
        ]
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Обзор'
        verbose_name_plural = 'Обзоры'
        ordering = (
            '-pub_date',
        )


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Обзор',
    )
    text = models.TextField('Текст')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор',
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = (
            '-pub_date',
        )
