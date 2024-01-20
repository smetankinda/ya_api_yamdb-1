from django.http import HttpRequest
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.serializers import (CharField, CurrentUserDefault,
                                        EmailField, IntegerField,
                                        ModelSerializer, RegexField,
                                        SlugRelatedField, ValidationError)
from rest_framework.validators import UniqueValidator

from reviews.models import Category, Comments, Genre, Review, Title, User


class UsersSerializer(ModelSerializer):
    """ Сериализатор для работы со списками пользователей. """

    username = RegexField(
        r'^[\w.@+-]+\Z$', max_length=150,
        required=True, validators=[
            UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )


class TokenSerializer(ModelSerializer):
    """ Сериализатор для работы с токенами и кодами подтверждения. """

    username = RegexField(r'^[\w.@+-]+\Z$', max_length=150)
    confirmation_code = CharField(
        required=True,
        max_length=36
    )

    class Meta:
        model = User
        fields = (
            'username',
            'confirmation_code'
        )


class GenreSerializer(ModelSerializer):
    """ Сериализатор для работы с жанрами. """

    class Meta:
        model = Genre
        exclude = ['id', ]
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }


class CategorySerializer(ModelSerializer):
    """ Сериализатор для работы с категориями. """

    class Meta:
        model = Category
        fields = ('name', 'slug')
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }


class TitleSerializer(ModelSerializer):
    """ Сериализатор для работы с произведениями (только чтение). """

    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = IntegerField(source='reviews__score__avg', read_only=True)

    class Meta:
        fields = ('id', 'genre', 'category', 'name', 'year',
                  'description', 'rating',)
        model = Title


class TitleSerializerPost(ModelSerializer):
    """ Сериализатор для работы с произведениями (изменение). """

    category = SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )
    genre = SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True
    )
    rating = IntegerField(source='reviews__score__avg', read_only=True)

    class Meta:
        fields = ('id', 'genre', 'category', 'name', 'year',
                  'description', 'rating',)
        model = Title


class SignupSerializer(ModelSerializer):
    """ Сериализатор для работы с регистрациями. """

    username = RegexField(r'^[\w.@+-]+\Z$', max_length=150)
    email = EmailField(required=True, max_length=254)

    class Meta:
        model = User
        fields = ('email', 'username')

    def validate(self, data):
        if data['username'].lower() == 'me':
            raise ValidationError(
                'Использовать имя <me> в качестве username запрещено'
            )
        current_email = User.objects.filter(email=data['email']).first()
        current_user = User.objects.filter(username=data['username']).first()

        if current_email and current_email.username != data['username']:
            raise ValidationError('Email не соответствует')

        if current_user and current_user.email != data['email']:
            raise ValidationError('Username не соответствует')
        return data


class ReviewSerializer(ModelSerializer):
    """ Сериализатор для работы с отзывами. """

    title = SlugRelatedField(
        slug_field='name',
        read_only=True,
    )
    author = SlugRelatedField(
        slug_field='username',
        default=CurrentUserDefault(),
        read_only=True
    )
    score = IntegerField(
        min_value=1,
        max_value=10
    )

    class Meta:
        model = Review
        fields = ('author', 'title', 'id', 'text', 'pub_date', 'score')

    def get_title(self, request: HttpRequest):
        return get_object_or_404(
            Title,
            pk=self.context.get('view').kwargs.get('title_id'),
        )

    def get_author(self, request: HttpRequest):
        return self.context.get('request').user

    def validate(self, data):
        if self.context.get('request').method == 'POST':
            if Review.objects.filter(
                    title=self.get_title(self),
                    author=self.get_author(self),
            ).exists():
                raise ValidationError(
                    'Нельзя оставлять отзыв на одно произведение дважды.',
                )
        return data


class CommentSerializer(ModelSerializer):
    """ Сериализатор для работы с комментариями. """

    author = SlugRelatedField(
        slug_field='username',
        default=CurrentUserDefault(),
        read_only=True
    )
    review = SlugRelatedField(
        slug_field='text',
        read_only=True
    )

    class Meta:
        model = Comments
        fields = ('author', 'review', 'id', 'text', 'pub_date')
