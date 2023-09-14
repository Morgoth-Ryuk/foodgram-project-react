from django.db.models import Model
from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAuthenticatedOrReadOnly(BasePermission):
    """Права на доступ авторизованным юзерам либо только на чтение."""
    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
        )


class AuthorStaffOrReadOnly(BasePermission):
    """
    Разрешение на изменение только для служебного персонала и автора.
    Остальным только чтение объекта.
    """

    def has_object_permission(self, request, view, obj: Model):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_active
            and (request.user == obj.author or request.user.is_staff)
        )


class AdminOrReadOnly(BasePermission):
    """
    Разрешение на создание и изменение только для админов.
    Остальным только чтение объекта.
    """

    def has_object_permission(self, request, view, pk):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_active
            and request.user.is_staff
        )


class OwnerUserOrReadOnly(BasePermission):
    """
    Разрешение на создание и изменение только для админа и пользователя.
    Остальным только чтение объекта.
    """

    def has_object_permission(self, request, view, obj: Model):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_active
            and request.user == obj.author
            or request.user.is_staff
        )
