from rest_framework.permissions import IsAuthenticatedOrReadOnly, BasePermission


class IsAdAuthorOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True

        return obj.author == request.user


class IsProposalAuthorOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True

        return obj.sender.author == request.user
