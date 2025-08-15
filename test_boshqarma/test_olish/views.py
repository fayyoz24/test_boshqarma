from rest_framework import viewsets, permissions, generics
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from .serializers import TestSessionSerializer, QuestionSerializer, OptionSerializer, QuestionCreateSerializer
from .models import TestResult, TestSession, Subject, Question, Option, StudentAnswer
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .serializers import AnswersListSerializer
import random
from rest_framework.views import APIView
from rest_framework.response import Response

from corecode.models import Class
from students.models import Student
from users.models import User
import string
from corecode.custom_permission import IsPaidUserPermissionForTheme


class CreateTestSessionView(APIView):
    queryset = TestSession.objects.all()
    serializer_class = TestSessionSerializer
    permission_classes = [permissions.IsAuthenticated, IsPaidUserPermissionForTheme]

    def get(self, request, subject_id):
        """
        Start a new test session for a given subject
        """

        subject = Subject.objects.get(id=subject_id)
        try:
            test_session = TestSession.objects.get(
                user=self.request.user, 
                subject_id=subject_id  # This ensures we check the specific theme
            )
            print("*"*30)
            print(test_session.is_completed)
            if test_session.is_completed:
                return Response({"detail": "You had that test before!"}, status=200)
        except Exception as e:
            test_session = TestSession.create_new_test_session(request.user, subject)
        
        serializer = self.serializer_class(test_session)
        return Response(serializer.data)
    

class TestResultsView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, test_session_id):
        test_session = TestSession.objects.get(id=test_session_id)
        student_answers = AnswersListSerializer(data=request.data)
        print("test_session"*30)
   # Check if test result already exists
        existing_test_result = TestResult.objects.filter(
            test_session=test_session, 
            test_session__user=request.user,
            test_session__is_completed=True
        ).first()
        print("test"*30)
        if existing_test_result:
            print("tesssssssst"*30)
            return Response({
                'message': 'You already completed this test',
                'score': existing_test_result.total_score,
                'passed': existing_test_result.passed,
                "subject": test_session.subject.name,
                "total_questions": existing_test_result.total_questions,
                "correct_answers": existing_test_result.correct_answers,
                "incorrect_answers": existing_test_result.total_questions - existing_test_result.correct_answers
            }, status=400)
        
        if student_answers.is_valid():
            try:
                test_result = TestResult.objects.get(
                    test_session=test_session, 
                    test_session__is_completed=True, 
                    test_session__user=request.user
                )
                test_result.calculate_score()
            except Exception:
                test_result = TestResult.objects.create(
                    test_session=test_session,
                    total_score=0,
                    passed=False
                )
            
            # Process student answers
            unanswered_count = 0
            for answer_data in student_answers.validated_data['answers']:
                question = Question.objects.get(id=answer_data['question_id'])
                
                # Handle blank answers
                if not answer_data.get('selected_option_id'):
                    unanswered_count += 1
                    StudentAnswer.objects.create(
                        test_result=test_result,
                        question=question,
                        selected_option=None,
                        is_correct=False  # Unanswered is considered incorrect
                    )
                else:
                    selected_option = Option.objects.get(id=answer_data['selected_option_id'])
                    StudentAnswer.objects.create(
                        test_result=test_result,
                        question=question,
                        selected_option=selected_option,
                        is_correct=selected_option.is_correct
                    )
            
            # Calculate final score
            test_result.calculate_score()
            
            # Mark test session as completed
            test_session.is_completed = True
            test_session.save()
            
            return Response({
                'score': test_result.total_score,
                'passed': test_result.passed,
                "subject": test_session.subject.name,
                "total_questions": test_result.total_questions,
                "correct_answers": test_result.correct_answers,
                "incorrect_answers": test_result.total_questions - test_result.correct_answers
            })
        
        return Response({"detail": student_answers.errors}, status=400)

class SubjectTestHistoryView(APIView):
    permission_classes=[IsAuthenticated]

    def get(self, request, subject_id):

        """
        Get test history for each theme in the subject,
        assuming one session per theme
        """
        subject = get_object_or_404(Subject, id=subject_id)
        
        # Get themes that have completed test sessions
        themes = Theme.objects.filter(
            subject=subject,
            testsession__user=request.user,
            testsession__is_completed=True,
            testsession__testresult__isnull=False
        ).distinct().prefetch_related(
            'testsession_set',
            'testsession_set__testresult',
            'testsession_set__testresult__student_answers'
        )
        
        serializer = ThemeTestHistorySerializer(
            themes, 
            many=True,
            context={'request': request}
        )
        
        return Response({
            'subject_id': subject.id,
            'subject_name': subject.name,
            'themes': serializer.data
        })


class FakeQuestionOptionAPIView(APIView):
    def post(self, request, *args, **kwargs):
        """
        Generate fake questions and options dynamically.
        """
        # Question.objects.all().delete()
        # Option.objects.all().delete()
        # Get the number of questions and options from the request or set defaults
        num_questions = request.data.get('num_questions', 100)
        num_options = request.data.get('num_options', 4)
        subject_theme_id = request.data.get('subject_theme_id', 1)

        fake_data = []
        try:
            theme = Theme.objects.get(id=int(subject_theme_id))
            print(subject_theme_id)
        except:
            return Response({"deatil": subject_theme_id}, status=200)
        for _ in range(num_questions):
            # Create a fake question
            question = Question.objects.create(
                theme=theme,
                title=fake.sentence(),
                image=None,  # Replace with a real image path if needed
            )

            for i in range(num_options):
                k = False
                if i==2:
                    k = True
                # Create fake options
                option = Option.objects.create(
                    question=question,
                    title=fake.sentence(),
                    image=None,  # Replace with a real image path if needed
                    is_correct=k,  # Randomly assign correct answers
                )

        return Response(fake_data, status=200)
    
class DeleteTestSessionView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        TestSession.objects.get(id=pk).delete()

        return Response({"detail":'Successfully deleted!'}, status=204)

class FakeUserCreateView(APIView):
    def get(self, request):
        class_=Class.objects.create(name='5 A')
        # User.objects.all().delete()
        # # try:
        letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
        # print(letters)
        for let in letters:
            print(let)
            user = User.objects.get(username=let)
            Student.objects.create(user=user, first_name=user.username, current_class = class_)
            # user.set_password(let)
            # user.save()
        # except:
        #     print("n"*76)

        return Response ({"detail" :"users are created"}, status=200)

from django.db.models import Avg, Count, Case, When, F
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ClassTestResultsBySubjectThemeSerializer, StudentThemeResultSerializer

class ResultsByClassSubjectThemes(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, class_id, subject_id):
        try:
            teacher = request.user.teacher
            if not teacher.teaching_classes.filter(id=class_id).exists() or teacher.subject.id != subject_id:
                return Response(
                    {"detail": "You don't have access to this class or subject"},
                    status=status.HTTP_403_FORBIDDEN
                )

            class_obj = Class.objects.get(id=class_id)
            if not class_obj.subjects.filter(id=subject_id).exists():
                return Response(
                    {"detail": "Subject not found in this class"},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Get themes for this class and subject
            themes = Theme.objects.filter(
                class_name_id=class_id,
                subject_id=subject_id
            )

            results = []
            for theme in themes:
                # Get all completed test sessions for this theme
                test_sessions = TestSession.objects.filter(
                    theme=theme,
                    is_completed=True
                ).select_related('test_result')

                # Calculate statistics if there are test results
                if test_sessions.exists():
                    test_results = TestResult.objects.filter(
                        test_session__in=test_sessions
                    )
                    
                    avg_score = test_results.aggregate(Avg('total_score'))['total_score__avg']
                    total_tested_students = test_results.count()
                    passed_students = test_results.filter(passed=True).count()
                    # passing_rate = (passing_tests / total_tests * 100) if total_tests > 0 else 0
    # total_tested_students = serializers.IntegerField()
    # passing_students = serializers.IntegerField()
                    theme_data = {
                        'theme_name': theme.name,
                        'theme_related_topics':theme.related_topics,
                        'average_score': round(avg_score, 2) if avg_score else 0,
                        'total_tested_students': total_tested_students,
                        'passing_students': passed_students,
                        'class_name': class_obj.name,
                        'subject_name': theme.subject.name
                    }
                    results.append(theme_data)

            serializer = ClassTestResultsBySubjectThemeSerializer(results, many=True)
            return Response(serializer.data)

        except Class.DoesNotExist:
            return Response(
                {"detail": "Class not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except Class.DoesNotExist:
            return Response(
                {"detail": "Class not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        


class ResultsByClassSubjectThemes(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, class_id, subject_id):
        try:
            # Permission checks remain the same
            teacher = request.user.teacher
            if not teacher.teaching_classes.filter(id=class_id).exists() or teacher.subject.id != subject_id:
                return Response(
                    {"detail": "You don't have access to this class or subject"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Get class and check subject relationship
            class_obj = Class.objects.get(id=class_id)
            if not class_obj.subjects.filter(id=subject_id).exists():
                return Response(
                    {"detail": "Subject not found in this class"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Updated filter to use class_name with M2M relationship
            themes = Theme.objects.filter(
                class_name=class_id,  # Changed from class_name_id
                subject_id=subject_id
            )
            
            # Rest of the code remains the same
            results = []

            for theme in themes:
                # Get all completed test sessions for this theme
                test_sessions = TestSession.objects.filter(
                    theme=theme,
                    is_completed=True
                ).select_related('test_result')

                # Calculate statistics if there are test results
                if test_sessions.exists():
                    test_results = TestResult.objects.filter(
                        test_session__in=test_sessions
                    )
                    
                    avg_score = test_results.aggregate(Avg('total_score'))['total_score__avg']
                    total_tested_students = test_results.count()
                    passed_students = test_results.filter(passed=True).count()
                    # passing_rate = (passing_tests / total_tests * 100) if total_tests > 0 else 0
    # total_tested_students = serializers.IntegerField()
    # passing_students = serializers.IntegerField()
                    theme_data = {
                        'theme_name': theme.name,
                        'theme_related_topics':theme.related_topics,
                        'average_score': round(avg_score, 2) if avg_score else 0,
                        'total_tested_students': total_tested_students,
                        'passing_students': passed_students,
                        'class_name': class_obj.name,
                        'subject_name': theme.subject.name
                    }
                    results.append(theme_data)

            serializer = ClassTestResultsBySubjectThemeSerializer(results, many=True)
            return Response(serializer.data)

        except Class.DoesNotExist:
            return Response(
                {"detail": "Class not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except Class.DoesNotExist:
            return Response(
                {"detail": "Class not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ThemeStudentResultsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, theme_id):
        try:
            theme = Theme.objects.get(id=theme_id)
            
            test_sessions = TestSession.objects.filter(
                theme_id=theme_id,
                is_completed=True
            ).select_related(
                'user',
                'user__student',
                'testresult'
            )

            results = []
            for session in test_sessions:
                try:
                    test_result = session.testresult
                    
                    student_name = f"{session.user.student.first_name.strip()} {session.user.student.last_name.strip()}"
                    
                    student_data = {
                        'student_name': student_name,
                        'test_score': round(test_result.total_score, 1),
                        'correct_answers':test_result.correct_answers,
                        'status': test_result.passed, 
                        'topics_to_improve': theme.related_topics,
                        'completed_at': test_result.completed_at
                    }
                    results.append(student_data)

                except TestResult.DoesNotExist:
                    continue

            results.sort(key=lambda x: x['student_name'])
            serializer = StudentThemeResultSerializer(results, many=True)
            return Response(serializer.data)

        except Theme.DoesNotExist:
            return Response(
                {"detail": "Theme not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

from .serializers import SchoolSubjectAverageSerializer
class SchoolSubjectAveragesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            director = request.user.director
            school = director.school

            subjects = Subject.objects.filter(
                class__shcool=school
            ).distinct()

            results = []
            for subject in subjects:
                # Updated filter for themes to handle M2M relationship
                test_results = TestResult.objects.filter(
                    test_session__theme__subject=subject,
                    test_session__theme__class_name__in=Class.objects.filter(shcool=school),  # Updated filter
                    test_session__is_completed=True
                )

                if test_results.exists():
                    avg_score = test_results.aggregate(
                        avg_score=Avg('total_score')
                    )['avg_score']

                    subject_data = {
                        'subject': subject,
                        'average_results': round(avg_score, 1) if avg_score else 0
                    }
                    results.append(subject_data)

            serializer = SchoolSubjectAverageSerializer(results, many=True)
            return Response(serializer.data)

        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )