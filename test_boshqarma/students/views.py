from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Student
from .serializers import SubjectSerializer, StudentClassSerializer
from corecode.models import Class
from rest_framework.views import APIView
from .serializers import StudentDetailSerilizer, StudentSubjectSerializer, StudentClassSerializer, TestHistorySerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from test_olish.models import TestSession
from corecode.models import Subject
from users.models import User
from users.utils import username_generator
from django.shortcuts import get_object_or_404
from corecode.models import School
import pandas as pd


class StudentDetailView(generics.RetrieveAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class = StudentDetailSerilizer

    def get_object(self):
        student = get_object_or_404(Student, user=self.request.user)
        return student

class StudentTestHistoryView(APIView):
    def get(self, request, subject_id):
        # Get the subject
        subject = get_object_or_404(Subject, id=subject_id)
        
        # Get all completed test sessions for this user and subject
        test_sessions = TestSession.objects.filter(
            user=request.user,
            subject=subject,
            is_completed=True,
            testresult__isnull=False  # Ensure test result exists
        ).select_related('testresult').prefetch_related('testresult__student_answers')
        
        # Serialize the data
        serializer = TestHistorySerializer(test_sessions, many=True)
        return Response(serializer.data, status=200)

class AddStudentsByList(APIView):
    def get(self, request, school_id):
        df = pd.read_excel("/home/itclastertest/IT_KLASTER/klaster/students/8-sinf.xlsx")
        for i in range(2, 200):

            family_name = df['Unnamed: 2'][i].split(" ")[0]
            first_name = df['Unnamed: 2'][i].split(" ")[1]
            try:
                other_name = df['Unnamed: 2'][i].split(" ")[2] + " " + df['Unnamed: 2'][i].split(" ")[3]
            except:
                other_name = df['Unnamed: 2'][i].split(" ")[2]
            class_name = df['Unnamed: 1'][i].replace("-", " ")
            school = School.objects.get(id=school_id)
            class_, _ = Class.objects.get_or_create(name = class_name, school=school)
            username=username_generator(first_name.lower())
            user = User.objects.create(username=username, email=username+"@mail.ru")
            user.set_password(username)
            user.save()
            
            Student.objects.create(user=user, first_name=first_name, last_name=family_name,
                                   other_name=other_name,
                                   current_class=class_)

        return Response({"detail":"detail"}, status=200)
