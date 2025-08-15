from django.shortcuts import render
from rest_framework import generics
from .models import Subject, Class
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from users.check_user_type import IsAdmin, IsStudent, IsTeacher
from users.models import User
from users.utils import username_generator
from rest_framework import serializers
from rest_framework.response import Response
from students.models import Student
# Student adding and listing part:
from rest_framework.views import APIView
from test_olish.serializers import SubjectSerializer
from .models import MonthSession
from .custom_permission import IsPaidUserPermission
from .models import MonthSession
from myclick.models import UserSessionAccess
from .serializers import MonthSessionSerializer, MonthSessionGetSerializer

from students.views import get_object_or_404
# Second version
from .serializers import MonthSessionSerializer, MonthSessionGetSerializer

# subject adding and listing part


class SubjectListView(generics.ListAPIView):
    serializer_class=SubjectSerializer
    queryset = Subject.objects.all()
    # permission_classes = [IsAdminUser]

class StudentMonthSessionListView(APIView):
    """
    View for listing all MonthSessions where the student's class subjects are included
    """
    serializer_class = MonthSessionSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retrieve and serialize all MonthSession objects that include the student's class subjects
        """
        # Get the student related to the authenticated user
        try:
            student = request.user.student  # Assuming there's a one-to-one relationship
            student_class = student.current_class  # Assuming student has a class reference
        except Exception as e:
            return Response(
                {"error": f"No student profile or class found for this user: {e}"}, 
                status=404
            )
        
        # Find all sessions that include subjects available for the student's class
        month_sessions = MonthSession.objects.filter(
            subjects__in=student_class.subjects.all()
        ).distinct().prefetch_related(
            'subjects'
        )
        
        # Check which sessions are paid for
        for session in month_sessions:
            session.is_paid = UserSessionAccess.objects.filter(
                user=request.user,
                session=session
            ).exists()
        
        # Serialize the queryset
        serializer = self.serializer_class(
            month_sessions, 
            many=True, 
            context={'request': request, 'student': student}
        )
        
        # Return serialized data
        return Response(serializer.data, status=200)


class MonthSessionGetView(APIView):
    """
    View for retrieving a specific MonthSession with subjects
    Only accessible if the user has paid for the session
    """
    serializer_class = MonthSessionGetSerializer
    permission_classes = [IsAuthenticated, IsPaidUserPermission]

    def get(self, request, month_session_id):
        """
        Retrieve and serialize a specific MonthSession object with detailed information
        """
        # Get the student related to the authenticated user
        try:
            student = request.user.student
            student_class = student.current_class
        except Exception as e:
            return Response(
                {"error": f"No student profile found for this user: {e}"}, 
                status=404
            )
        
        # Verify the session has subjects for the student's class
        month_session = get_object_or_404(
            MonthSession.objects.filter(
                subjects__in=student_class.subjects.all()
            ).distinct().prefetch_related(
                'subjects',
            ),
            id=month_session_id
        )
        
        # Serialize the month session with detailed information
        serializer = self.serializer_class(
            month_session, 
            context={'request': request, 'student': student}
        )
        
        # Return serialized data
        return Response(serializer.data, status=200)

