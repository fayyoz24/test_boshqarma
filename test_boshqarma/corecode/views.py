from django.shortcuts import render
from .serializers import ClassAdminSerializer, SubjectAdminSerializer, MarkSerializer, ClassDetailSerializer, ClassUpdateSerializer, StudentClassmatesAdminSerializer
from rest_framework import generics
from .models import Subject, Class, Mark
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from users.check_user_type import IsAdmin, IsStudent, IsTeacher
from staffs.serializers import TeacherProfileSerializer
from staffs.models import Teacher
from users.models import User
from users.utils import username_generator
from rest_framework import serializers
from rest_framework.response import Response
from students.models import Student
# Student adding and listing part:
from rest_framework.views import APIView
from .serializers import StudentAdminSerializer
from test_olish.serializers import SubjectSerializer
from .models import MonthSession
from .custom_permission import IsPaidUserPermission
from .models import MonthSession
from myclick.models import UserSessionAccess
from .serializers import MonthSessionSerializer, MonthSessionGetSerializer

from students.views import get_object_or_404
# Second version
from .serializers import ClassDetailSerializer, MonthSessionSerializer, MonthSessionGetSerializer

# subject adding and listing part
class SubjectListCreateView(generics.ListCreateAPIView):
    serializer_class=SubjectAdminSerializer
    queryset = Subject.objects.all()
    permission_classes = [IsAdminUser]

class SubjectUpdateDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdmin]  # Uncomment if you need permission
    queryset = Subject.objects.all()
    lookup_field = 'id'  # or 'pk' depending on your URL pattern
    serializer_class = SubjectAdminSerializer

# teacher adding and listing part
class TeacherCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdmin]
    serializer_class = TeacherProfileSerializer
    queryset = Teacher.objects.all()

    def perform_create(self, serializer):
        first_name = self.request.data.get('first_name')
        last_name = self.request.data.get('last_name')
        subject_id = self.request.data.get('subject')  # Get subject ID from request
        
        if not subject_id:
            raise serializers.ValidationError({"subject": "Subject field is required"})
            
        username = username_generator(first_name)
        
        user = User.objects.create(
            username=username,
            user_type='TR'
        )
        user.set_password(last_name)
        user.save()
        
        # Associate both user and subject during teacher creation
        teacher = serializer.save(
            user=user,
            subject_id=subject_id
        )
        
        return teacher

# class creating and listing
class ClassListCreateView(generics.ListCreateAPIView):
    serializer_class=ClassAdminSerializer
    queryset = Class.objects.all()
    permission_classes = [IsAdminUser]

# class getting and updating
class ClassUpdateDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser] 
    queryset = Class.objects.all()
    lookup_field = 'id'  # or 'pk' depending on your URL pattern

    def get_serializer_class(self):
        # Use ClassDetailSerializer for GET and ClassUpdateSerializer for PUT/PATCH
        if self.request.method in ['PUT', 'PATCH']:
            return ClassUpdateSerializer
        return ClassDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class StudentListCreateView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, id):
        queryset = Student.objects.filter(current_class=id)
        serializer = StudentAdminSerializer(queryset, many=True)  # `many=True` for queryset
        return Response({"data": serializer.data}, status=200)
    
    def post(self, request, id):
        serializer = StudentAdminSerializer(data=request.data)
        if serializer.is_valid():
            first_name = serializer.validated_data['first_name']
            last_name = serializer.validated_data['last_name']
            try:
                mobile_number = serializer.validated_data['mobile_number']
            except:
                mobile_number=None
            # 'id', 'first_name', 'last_name', 'mobile_number'

            username = username_generator(first_name)
            user = User.objects.create(username=username, user_type = "ST")
            user.set_password(last_name)
            user.save()
            student = Student.objects.create(user=user, current_class=Class.objects.get(id=id), first_name=first_name, last_name=last_name, mobile_number=mobile_number)
            data = StudentAdminSerializer(student).data
            return Response({"data":data}, status=200)
        return Response(serializer.errors, status=400)


class StudenListView(APIView):
    permission_classes = [IsAdminUser]
    serializer_class = StudentClassmatesAdminSerializer

    def get(self, request, *args, **kwargs):
        queryset = Student.objects.all()
        return Response({"data":self.serializer_class(queryset, many=True).data})


class ClassDetailView(generics.RetrieveAPIView):
    serializer_class = ClassDetailSerializer
    permission_classes=[IsAuthenticated]

    def get_object(self):
        pk = self.kwargs.get("pk")
        class_detail = get_object_or_404(Class, id=pk)
        return class_detail
    

# list of sujects


class SubjectListView(generics.ListAPIView):
    serializer_class=SubjectSerializer
    queryset = Subject.objects.all()
    # permission_classes = [IsAdminUser]


# class MonthSessionView(APIView):
#     """
#     ViewSet for Sessions with nested Themes
#     """
#     serializer_class = MonthSessionSerializer
#     permission_classes = [IsAuthenticated]
    
#     def get(self, request):
#         """
#         Retrieve and serialize MonthSession objects
#         """
#         # Fetch MonthSession objects with prefetched themes
#         month_sessions = MonthSession.objects.prefetch_related(
#             'themes', 
#             'themes__subject'
#         )
        
#         # Serialize the queryset
#         serializer = self.serializer_class(
#             month_sessions, 
#             many=True, 
#             context={'request': request}
#         )
        
#         # Return serialized data
#         return Response(serializer.data, status=200)

# class MonthSessionGetView(APIView):
#     """
#     ViewSet for retrieving a specific MonthSession with nested Themes
#     """
#     serializer_class = MonthSessionGetSerializer
#     permission_classes = [IsAuthenticated, IsPaidUserPermission]

#     def get(self, request, month_session_id):
#         """
#         Retrieve and serialize a specific MonthSession object
#         """
#         # Fetch MonthSession object with prefetched themes
#         month_session = get_object_or_404(
#             MonthSession.objects.prefetch_related(
#                 'themes', 
#                 'themes__subject'
#             ),
#             id=id
#         )
        
#         # Serialize the month session
#         serializer = self.serializer_class(
#             month_session, 
#             context={'request': request}
#         )
        
#         # Return serialized data
#         return Response(serializer.data, status=200)
    




class StudentMonthSessionListView(APIView):
    """
    View for listing all MonthSessions where the student's class is included
    """
    serializer_class = MonthSessionSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retrieve and serialize all MonthSession objects that include the student's class
        """
        # Get the student related to the authenticated user
        try:
            student = request.user.student  # Assuming there's a one-to-one relationship
            student_class = student.current_class  # Assuming student has a class reference
            print(student_class)
        except Exception as e:
            return Response(
                {"error": f"No student profile or class found for this user {e}"}, 
                status=404
            )
        
        # Find all sessions that include themes available for the student's class
        month_sessions = MonthSession.objects.filter(
            themes__class_name=student_class
        ).distinct().prefetch_related(
            'themes', 
            'themes__subject'
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
    View for retrieving a specific MonthSession with nested Themes and questions
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
                {"error": f"No student profile found for this user {e}"}, 
                status=404
            )
        
        # Verify the session has themes for the student's class
        month_session = get_object_or_404(
            MonthSession.objects.filter(
                themes__class_name=student_class
            ).distinct().prefetch_related(
                'themes',
                'themes__subject',
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

# Example serializers (basic structure)

