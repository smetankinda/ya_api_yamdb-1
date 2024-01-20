from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from .constants import ADMIN, MODERATOR, OUTPUT_TEXT_LIMIT, ROLE_CHOICES, USER
from .validators import is_username_valid


class User(AbstractUser):
    """ Модель пользователя. """

    username = models.CharField(
        verbose_name='Логин',
        max_length=150,
        unique=True,
        validators=(is_username_valid,),
        help_text=('Необходимое поле для заполнения. Не более 150 символов.'
                   'Только буквы, цифры и символы @/./+/-/_.'),
        error_messages={
            'unique': ('Пользователь с таким именем уже существует.'),
        },
    )
    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=254,
        unique=True,
        blank=False,
        null=False,
    )
    bio = models.TextField(
        verbose_name='О себе',
        blank=True,
        help_text='Расскажите о себе',
    )
    role = models.CharField(
        verbose_name='Роль пользователя',
        max_length=10,
        choices=ROLE_CHOICES,
        default=USER,
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
        blank=True,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
        blank=True,
    )
    confirmation_code = models.CharField(
        verbose_name='Код подтверждения',
        max_length=36,
        blank=True,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    @property
    def is_user(self):
        return self.role == USER

    @property
    def is_admin(self):
        return self.role == ADMIN

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    def __str__(self) -> str:
        """Строковое представление объекта."""
        return self.username


class Category(models.Model):
    """ Модель категорий. """

    name = models.CharField(
        verbose_name='Название категории',
        max_length=256,
        blank=False,
        null=False,
    )
    slug = models.SlugField(
        verbose_name='Слаг категории',
        max_length=50,
        unique=True,
        db_index=True,
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ('name',)

    def __str__(self) -> str:
        """Строковое представление объекта."""
        return self.name


class Genre(models.Model):
    """ Модель жанров. """

    name = models.CharField(
        verbose_name='Название жанра',
        max_length=256,
        blank=False,
        unique=True,
    )
    slug = models.SlugField(
        verbose_name='Слаг жанра',
        max_length=50,
        blank=True,
        unique=True,
        db_index=True,
    )

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ('name',)

    def __str__(self) -> str:
        """Строковое представление объекта."""
        return self.name


class Title(models.Model):
    """ Модель произведений."""

    name = models.CharField(
        verbose_name='Название произведения',
        max_length=256,
        blank=False,
        null=False,
        db_index=True,
    )
    year = models.PositiveSmallIntegerField(
        verbose_name='Год издания',
        validators=[
            MinValueValidator(1500),
            MaxValueValidator(timezone.now().year)
        ],
        error_messages={'validators': 'Введите корректный год издания'},
        help_text='Введите год издания',
        db_index=True,
    )
    description = models.TextField(
        verbose_name='Описание',
        blank=True,
        null=True,
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        verbose_name='Категория',
        blank=True,
        null=True,
        db_index=True,
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        verbose_name='Жанр',
        db_index=True,
    )

    class Meta:
        verbose_name = 'Название произведения'
        verbose_name_plural = 'Названия произведений'
        ordering = ('name',)

    def __str__(self) -> str:
        """Строковое представление объекта."""
        return self.name


class Review(models.Model):
    """ Модель отзывов."""

    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Обзор произведения',
    )
    text = models.TextField(
        verbose_name='Текст отзыва',
        help_text='Оставьте свой отзыв о произведении',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор отзыва',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации отзыва',
        auto_now_add=True,
    )
    score = models.PositiveSmallIntegerField(
        verbose_name='Оценка',
        help_text='Введите оценку от 1 до 10',
        validators=[
            MinValueValidator(1, 'Значение не может быть меньше 1'),
            MaxValueValidator(10, 'Значение не может быть больше 10'),
        ],
        error_messages={'validators': 'Оценка должна быть от 1 до 10'}
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ('-pub_date',)
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='one-review-on-one-title'
            )
        ]

    def __str__(self) -> str:
        """Строковое представление объекта."""
        return self.text[:OUTPUT_TEXT_LIMIT]


class Comments(models.Model):
    """ Модель комментариев."""

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв',
    )
    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='Оставьте комментарий',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации комментария',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('-pub_date',)

    def __str__(self) -> str:
        """Строковое представление объекта."""
        return self.text[:OUTPUT_TEXT_LIMIT]
