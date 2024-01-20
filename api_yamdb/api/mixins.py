from rest_framework import mixins, viewsets


class CreateReadDeleteViewSet(mixins.ListModelMixin,
                              mixins.CreateModelMixin,
                              mixins.DestroyModelMixin,
                              viewsets.GenericViewSet):
    """Создание кастомного вьюсета для жанров и категорий """
    pass
