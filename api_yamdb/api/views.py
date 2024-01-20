import uuid

from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import Category, Genre, Review, Title, User

from .filters import TitleFilter
from .mixins import CreateReadDeleteViewSet
from .permissions import (IsAdminOrReadOnly, IsAdminOrSuperUser,
                          IsAuthorOrReadOnly)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer, SignupSerializer,
                          TitleSerializer, TitleSerializerPost,
                          TokenSerializer, UsersSerializer)


class UsersViewSet(ModelViewSet):
    """
    Получение писка пользователей.
    Права доступа:
     - Зарегистрированные пользователи или Администратор.
    """
    lookup_field = 'username'
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    filter_backends = (SearchFilter,)
    search_fields = ('username',)
    permission_classes = (IsAuthenticated, IsAdminOrSuperUser,)

    http_method_names = ('get', 'post', 'head', 'patch', 'delete',)

    @action(
        methods=('GET', 'PATCH',),
        url_path='me',
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def profile(self, request):
        if request.method == 'GET':
            serializer = UsersSerializer(
                request.user
            )
            return Response(serializer.data)

        serializer = UsersSerializer(
            request.user,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(role=request.user.role)
        return Response(serializer.data)


class CategoryViewSet(CreateReadDeleteViewSet):
    """
    Получить список всех категорий.
    Права доступа:
     - Чтение доступно без токена;
     - Изменение категорий -только Администратор и Суперюзер.
    """
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenreViewSet(CreateReadDeleteViewSet):
    """
    Получить список всех жанров.
    Права доступа:
     - Чтение доступно без токена;
     - Изменение жанров - только Администратор и Суперюзер.
    """
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class TitleViewSet(ModelViewSet):
    """
    Получить список всех произведений.
    Права доступа: Доступно без токена.
    """
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Title.objects.all().annotate(
        Avg('reviews__score')
    ).order_by('id')

    serializer_class = TitleSerializerPost
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve',):
            return TitleSerializer
        return TitleSerializerPost


class ReviewViewSet(ModelViewSet):
    """
    Получить список всех отзывов.
    Права доступа:
     - Чтение доступно без токена;
     - Изменение отзыва - только автор или Администратор.
    """
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorOrReadOnly,)

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            title=get_object_or_404(Title, id=self.kwargs.get('title_id'))
        )


class CommentViewSet(ModelViewSet):
    """
    Получить список всех комментариев.
    Права доступа:
     - Чтение доступно без токена;
     - Изменение комментария - только автор или Администратор.
    """
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrReadOnly,)

    def get_queryset(self):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        return review.comments.select_related('review')

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            review=get_object_or_404(
                Review,
                id=self.kwargs.get('review_id'),
                title=self.kwargs.get('title_id'),
            )
        )


class AuthSignup(APIView):
    """
    Регистрация пользователя
    и отправка кода подтверждения на адрес э/почты.
    """

    @staticmethod
    def post(request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, created = User.objects.get_or_create(
            username=serializer.validated_data['username'],
            email=serializer.validated_data['email'],
        )
        user.confirmation_code = uuid.uuid4()
        user.save

        send_mail(
            subject='Код подтверждения для проекта YaMDb',
            message=f'Уважаемый, {str(user.username)}! '
            f'Ваш код подтверждения: {user.confirmation_code}',
            from_email=None,
            recipient_list=[user.email],
            fail_silently=False,
        )
        return Response(serializer.data, status=HTTP_200_OK)


class AuthToken(APIView):
    """ Получение и обновление токена. """

    @staticmethod
    def post(request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user = get_object_or_404(User, username=data['username'])
        if user.confirmation_code != data['confirmation_code']:
            return Response(
                {'confirmation_code': 'Неверный код подтверждения'},
                status=HTTP_400_BAD_REQUEST
            )
        token = RefreshToken.for_user(user).access_token
        return Response({'token': str(token)},
                        status=HTTP_200_OK)
