from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from students.models import Student
from .serializers import TeacherProfileSerializer, TeacherMarkClassSerializer
from corecode.models import Mark, Class
from .models import Teacher
from rest_framework import serializers
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from users.check_user_type import IsTeacher, IsAdmin
from django_filters import rest_framework as filters
from .serializers import MarkGetSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Avg, Q
from .permission_mixin import KattakonPermissionMixin
from corecode.models import Tuman
from test_olish.models import TestSession, TestResult
from .models import Kattakon
from .serializers import KattakonAnalyticsSerializer, TumanAnalyticsSerializer
from django.db.models.functions import Coalesce
from django.db.models import Count, Avg, Q, F
from django.db.models.functions import Coalesce
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Count, F, Window
from corecode.models import Subject

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Avg, Q
from django.db.models.functions import Coalesce

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Avg, Q
from django.db.models.functions import Coalesce
from corecode.models import School


# Create your views here.

class TeacherProfileView(generics.RetrieveAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class = TeacherProfileSerializer
    def get_object(self):
        teacher = get_object_or_404(Teacher, user=self.request.user)
        # print(f"class {student.current_class}")
        return Teacher.objects.get(id = teacher.id)


# class TeacherMarkClassView(generics.CreateAPIView):
#     permission_classes = [IsTeacher]  # Using our custom permission class
#     serializer_class = TeacherMarkClassSerializer

#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data, context={'request': request})
        
#         if serializer.is_valid():
#             teacher = request.user.teacher
#             marks_data = serializer.validated_data
            
#             # Create mark entries for each student
#             marks_to_create = []
#             for mark_entry in marks_data['marks_list']:
#                 mark = Mark(
#                     subject_id=marks_data['subject_id'],
#                     class_instance_id = marks_data['class_id'],
#                     teacher=teacher,
#                     marked_at=marks_data['marked_at'],
#                     student_id=mark_entry['student_id'],
#                     is_present=mark_entry['is_present'],
#                     homework_score=mark_entry['homework_score'],
#                     classwork_score=mark_entry['classwork_score']
#                 )
#                 marks_to_create.append(mark)

#             try:
#                 # Bulk create all marks
#                 Mark.objects.bulk_create(marks_to_create)
#                 return Response({
#                     'detail': 'Marks submitted successfully',
#                     'subject_id': marks_data['subject_id'],
#                     'count': len(marks_to_create)
#                 }, status=status.HTTP_201_CREATED)
                
#             except Exception as e:
#                 return Response({
#                     'detail': 'Error submitting marks',
#                     'detail': str(e)
#                 }, status=status.HTTP_400_BAD_REQUEST)

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class MarkFilter(filters.FilterSet):
#     subject = filters.NumberFilter(field_name='subject__id')
#     class_id= filters.NumberFilter(field_name='class_instance__id')
#     start_date = filters.DateFilter(field_name='marked_at', lookup_expr='gte')
#     end_date = filters.DateFilter(field_name='marked_at', lookup_expr='lte')

#     class Meta:
#         model = Mark
#         fields = ['subject', 'class_id', 'start_date', 'end_date']

# class TeacherMarksView(generics.ListAPIView):
#     serializer_class = MarkGetSerializer
#     permission_classes = [IsTeacher]
#     filter_backends = (filters.DjangoFilterBackend,)
#     filterset_class = MarkFilter

#     def get_queryset(self):
#         teacher = self.request.user.teacher  # Assuming the user has a related teacher profile
#         return Mark.objects.filter(
#             teacher=teacher,
#             subject=teacher.subject,
#             class_instance__in=teacher.teaching_classes.all()
#         ).select_related('student', 'subject', 'class_instance').order_by('-marked_at')



class DashboardAnalyticsView(APIView, KattakonPermissionMixin):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Get comprehensive analytics for Kattakon dashboard
        """
        # Check if user is Kattakon
        kattakon_check = self.check_kattakon(request)
        if kattakon_check:
            return kattakon_check
        try:
            analytics = request.user.kattakon.get_analytics()
            serializer = KattakonAnalyticsSerializer(analytics)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=500
            )


class TumanAnalyticsBySubjectView(APIView, KattakonPermissionMixin):
    def get(self, request):
        kattakon_check = self.check_kattakon(request)
        if kattakon_check:
            return kattakon_check
        
        subject_id = request.query_params.get('subject_id')
        
        if not subject_id:
            return Response(
                {'error': 'subject_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            subject = Subject.objects.get(id=subject_id)
        except Subject.DoesNotExist:
            return Response(
                {'error': 'Subject not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

        tumans = Tuman.objects.annotate(
            student_count=Count(
                'school__class__student',
                filter=Q(school__class__subjects=subject),
                distinct=True
            ),
            tested_count=Count(
                'school__class__student__user__testsession',
                filter=Q(school__class__student__user__testsession__theme__subject=subject),
                distinct=True
            ),
            passed_count=Count(
                'school__class__student__user__testsession__testresult',
                filter=Q(
                    school__class__student__user__testsession__theme__subject=subject,
                    school__class__student__user__testsession__testresult__passed=True
                ),
                distinct=True
            ),
            average_score=Coalesce(
                Avg(
                    'school__class__student__user__testsession__testresult__total_score',
                    filter=Q(school__class__student__user__testsession__theme__subject=subject)
                ),
                0.0
            )
        )

        total_students = sum(tuman.student_count for tuman in tumans)
        total_tested = sum(tuman.tested_count for tuman in tumans)
        total_passed = sum(tuman.passed_count for tuman in tumans)
        
        total_scores = sum(tuman.average_score * tuman.tested_count for tuman in tumans)
        average_score = round(total_scores / total_tested, 1) if total_tested > 0 else 0.0

        tuman_list = [{"subject": subject.name}]
        
        for tuman in tumans:
            tuman_list.append({
                "id": tuman.id,
                "name": tuman.name,
                "student_count": tuman.student_count,
                "tested_count": tuman.tested_count,
                "passed_count": tuman.passed_count,
                "average_score": float(tuman.average_score)
            })
            
        return Response({
            "tumans": tuman_list,
            "total_students": total_students,
            "total_tested": total_tested,
            "total_passed": total_passed,
            "average_score": average_score
        })
        

class SchoolAnalyticsBySubjectView(APIView, KattakonPermissionMixin):
    def get(self, request):

        kattakon_check = self.check_kattakon(request)
        if kattakon_check:
            return kattakon_check
        
        subject_id = request.query_params.get('subject_id')
        tuman_id = request.query_params.get('tuman_id')
        try:
            tuman = Tuman.objects.get(id=tuman_id)
        except Tuman.DoesNotExist:
            return Response(
                {'error': 'Tuman not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
            
        subject = None
        if subject_id:
            try:
                subject = Subject.objects.get(id=subject_id)
            except Subject.DoesNotExist:
                return Response(
                    {'error': 'Subject not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )

        # Base filter for the tuman
        base_filter = Q(tuman=tuman)
        subject_filter = Q(class__subjects=subject) if subject else Q()

        schools = School.objects.filter(base_filter).annotate(
            student_count=Count(
                'class__student',
                filter=subject_filter,
                distinct=True
            ),
            tested_count=Count(
                'class__student__user__testsession',
                filter=Q(class__student__user__testsession__theme__subject=subject) if subject else Q(),
                distinct=True
            ),
            passed_count=Count(
                'class__student__user__testsession__testresult',
                filter=Q(
                    class__student__user__testsession__theme__subject=subject,
                    class__student__user__testsession__testresult__passed=True
                ) if subject else Q(),
                distinct=True
            ),
            average_score=Coalesce(
                Avg(
                    'class__student__user__testsession__testresult__total_score',
                    filter=Q(class__student__user__testsession__theme__subject=subject) if subject else Q()
                ),
                0.0
            )
        )

        total_students = sum(school.student_count for school in schools)
        total_tested = sum(school.tested_count for school in schools)
        total_passed = sum(school.passed_count for school in schools)
        
        total_scores = sum(school.average_score * school.tested_count for school in schools)
        average_score = round(total_scores / total_tested, 1) if total_tested > 0 else 0.0

        # Format response
        school_list = [{"subject": subject.name if subject else "All subjects"}]
        
        for school in schools:
            school_list.append({
                "id": school.id,
                "name": school.name,
                "student_count": school.student_count,
                "tested_count": school.tested_count,
                "passed_count": school.passed_count,
                "average_score": float(school.average_score)
            })
            
        return Response({
            "schools": school_list,
            "total_students": total_students,
            "total_tested": total_tested,
            "total_passed": total_passed,
            "average_score": average_score
        })




class SubjectAnalyticsView(APIView, KattakonPermissionMixin):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        subject_id = request.query_params.get('subject_id')
        if not subject_id:
            return Response(
                {'detail': 'subject_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Aggregate analytics at the subject and tuman levels
            tumans = Tuman.objects.annotate(
                student_count=Count('school__class__student', distinct=True),
                tested_count=Count(
                    'school__class__student__user__testsession__testresult',
                    filter=Q(school__class__students__current_class__subjects__id=subject_id),
                    distinct=True
                ),
                passed_count=Count(
                    'school__class__student__user__testsession__testresult',
                    filter=Q(
                        school__class__student__user__testsession__testresult__passed=True,
                        school__class__students__current_class__subjects__id=subject_id
                    ),
                    distinct=True
                ),
                average_score=Coalesce(
                    Avg(
                        'school__class__student__user__testsession__testresult__total_score',
                        filter=Q(school__class__students__current_class__subjects__id=subject_id)
                    ),
                    0.0
                )
            )

            # Prepare the response data
            tuman_results = []
            total_students = 0
            total_tested = 0
            total_passed = 0
            total_scores = 0

            for tuman in tumans:
                tuman_results.append({
                    'id': tuman.id,
                    'name': tuman.name,
                    'student_count': tuman.student_count,
                    'tested_count': tuman.tested_count,
                    'passed_count': tuman.passed_count,
                    'average_score': round(tuman.average_score, 2) if tuman.average_score else 0.0
                })

                total_students += tuman.student_count
                total_tested += tuman.tested_count
                total_passed += tuman.passed_count
                total_scores += tuman.average_score * tuman.tested_count if tuman.tested_count else 0

            # Calculate overall pass rate
            overall_pass_rate = round((total_passed / total_tested * 100), 1) if total_tested > 0 else 0.0
            
            # Calculate overall average score
            overall_average_score = round(total_scores / total_tested, 2) if total_tested > 0 else 0.0

            return Response({
                'subject_id': subject_id,
                'total_students': total_students,
                'total_tested': total_tested,
                'total_passed': total_passed,
                'overall_pass_rate': overall_pass_rate,
                'tuman_results': tuman_results
            })

        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )