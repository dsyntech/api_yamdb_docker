from rest_framework.permissions import BasePermission, SAFE_METHODS

from .models import ROLE_MODERATOR, ROLE_ADMIN


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and (request.user.role == ROLE_ADMIN
                 or request.user.is_superuser
                 or request.user.is_staff)
        )


class IsAdminOrReadOnly(IsAdmin):
    def has_permission(self, request, view):
        return (request.method in SAFE_METHODS
                or super().has_permission(request, view))


class IsAuthorOrModeratorOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS
                or request.user.is_authenticated
                and (obj.author == request.user
                     or request.user.role == ROLE_MODERATOR))
