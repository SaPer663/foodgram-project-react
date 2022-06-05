from rest_framework.permissions import SAFE_METHODS, BasePermission


class AuthorOrReadOnly(BasePermission):
    """Разрешение на изменения только автору."""
    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS
            and request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return request.user == obj.author
