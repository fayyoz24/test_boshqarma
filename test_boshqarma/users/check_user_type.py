from rest_framework.permissions import IsAuthenticated
from .models import User


def get_user_type_display(user):
    return dict(User.USER_TYPE_CHOICES)[user.user_type]

class IsTeacher(IsAuthenticated):
    def has_permission(self, request, view):
        is_authenticated = super().has_permission(request, view)
        return is_authenticated and request.user.user_type == User.TEACHER
    
class IsStudent(IsAuthenticated):
    def has_permission(self, request, view):
        is_authenticated = super().has_permission(request, view)
        return is_authenticated and request.user.user_type == User.STUDENT
    
class IsAdmin(IsAuthenticated):
    def has_permission(self, request, view):
        is_authenticated = super().has_permission(request, view)
        return is_authenticated and request.user.user_type == User.ADMIN