from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import BasePermission
from django.shortcuts import get_object_or_404
from myclick.models import UserSessionAccess
from corecode.models import Theme


class IsPaidUserPermission(BasePermission):
    """
    Custom permission to only allow access to paid users
    """
    def has_permission(self, request, view):
        month_session_id = view.kwargs.get('month_session_id')
        print(month_session_id)
        print(UserSessionAccess.objects.filter(
            user=request.user,
            session_id=month_session_id
        ))
        # Check if user has access through UserSessionAccess
        return UserSessionAccess.objects.filter(
            user=request.user,
            session_id=month_session_id
        ).exists()
    

class IsPaidUserPermissionForTheme(BasePermission):
    """
    Custom permission to only allow access to themes that belong to a paid session
    """
    def has_permission(self, request, view):
        theme_id = view.kwargs.get('subject_theme_id')
        
        try:
            # Get the theme
            theme = Theme.objects.get(id=theme_id)
            
            # Find which sessions this theme belongs to
            session_ids = theme.monthsessions.all().values_list('id', flat=True)
            
            # Check if user has access to any of these sessions
            has_access = UserSessionAccess.objects.filter(
                user=request.user,
                session_id__in=session_ids
            ).exists()
            
            return has_access
            
        except Theme.DoesNotExist:
            return False
        except Exception as e:
            # Log the error for debugging
            print(f"Permission check error: {e}")
            return False