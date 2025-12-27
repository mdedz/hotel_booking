from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj) -> bool:
        if request.user and request.user.is_staff:
            return True
        return getattr(obj, "user", None) == request.user
