from rest_framework.permissions import BasePermission

class IsTeacherUser(BasePermission):
    """
    Allows access only to admin users.
    """

    def has_permission(self, request, view):
        return bool(request.user.user and request.user.is_staff)
