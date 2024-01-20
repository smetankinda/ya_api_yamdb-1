from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (AuthSignup, AuthToken, CategoryViewSet, CommentViewSet,
                       GenreViewSet, ReviewViewSet, TitleViewSet, UsersViewSet)

router_v1 = DefaultRouter()

router_v1.register('users', UsersViewSet, basename='users')
router_v1.register('categories', CategoryViewSet, basename='category')
router_v1.register('genres', GenreViewSet, basename='genres')
router_v1.register('titles', TitleViewSet, basename='titles')

router_v1.register(
    'titles/(?P<title_id>[0-9]+)/reviews/(?P<review_id>[0-9]+)/comments',
    CommentViewSet,
    basename='comments',
)

router_v1.register(
    'titles/(?P<title_id>[0-9]+)/reviews',
    ReviewViewSet,
    basename='reviews',
)

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/auth/signup/', AuthSignup.as_view(), name='signup'),
    path('v1/auth/token/', AuthToken.as_view(), name='token'),
]
