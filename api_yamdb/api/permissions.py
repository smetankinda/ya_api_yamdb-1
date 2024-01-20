from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsOwnerOrReadOnly(BasePermission):
    """ Права владельца на редактирование, остальные только чтение. """

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or obj.owner == request.user
        )


class IsSuperUserOrReadOnly(BasePermission):
    """
    Права суперпользователя на редактирование,
    остальные - только чтение.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return (
            request.method in SAFE_METHODS
            or request.user.is_superuser
        )


class IsAdminOrReadOnly(BasePermission):
    """
    Права администратора на редактирование,
    остальные - только на чтение.
    """

    def has_permission(self, request, view):
        return (request.method in SAFE_METHODS
                or (request.user.is_authenticated
                    and request.user.is_admin))


class IsAdminOrSuperUser(BasePermission):
    """ Права администратора или суперпользователя. """

    def has_permission(self, request, view):
        return (
            request.user.is_admin
            or request.user.is_superuser
        )


class IsAuthorOrReadOnly(BasePermission):
    """
    Права владельца (автора) или всех администраторов на редактирование.
    Остальные - только чтение.
    """

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or obj.author == request.user
            or request.user.is_admin
            or request.user.is_superuser
            or request.user.is_moderator
        )
