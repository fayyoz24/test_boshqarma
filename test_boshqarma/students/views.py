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
import json


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


from myclick.models import UserSessionAccess
class AddStudentsByList(APIView):
    def get(self, request, school_id):
        # df = pd.read_excel("/home/itclastertest/IT_KLASTER/klaster/students/8-sinf.xlsx")
        df = pd.read_excel("students/aloqa.xlsx")
        with open("students/passwords.json", "r") as f:
            data = json.load(f)
        for i in range(5):
            class_name = 'Aloqabank'
            # family_name = df['Unnamed: 2'][i].split(" ")[0]
            first_name = df['Ismi'][i].split(" ")[0]
            phone_number = "+" + str(df['Telefon raqami'][i])
            school = School.objects.get(id=school_id)
            class_, _ = Class.objects.get_or_create(name = class_name, school=school)
            username=username_generator(first_name.lower())
            user = User.objects.create(username=username, email=username+"@mail.ru")
            user.set_password(phone_number)
            user.save()
            UserSessionAccess.objects.create(
                user=user,
                session_id=1  # Assuming session with ID 1 exists
            )
            new_user = {"username": username, "password": phone_number}
            data["users"].append(new_user)
            Student.objects.create(user=user, first_name=first_name, phone_number=phone_number,
                                   current_class=class_)

        with open("students/passwords.json", "w") as f:
            json.dump(data, f, indent=4)

        return Response({"detail":"detail"}, status=200)
