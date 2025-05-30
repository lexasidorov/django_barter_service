from rest_framework.permissions import IsAuthenticatedOrReadOnly, BasePermission


class IsAuthorOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Разрешить безопасные методы (GET, HEAD, OPTIONS) всем
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True

        return obj.author == request.user
