
from corecode.models import Subject, Mark, Class, Theme
from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework import serializers
from staffs.serializers import TeacherProfileSerializer
from .models import Student

# class StudentClassmatesSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Student
#         fields = ['id', 'first_name', 'last_name', 'gender', 'parent_mobile_number', 'address']
   

# class StudentClassSerializer(ModelSerializer):
#     subjects = SubjectSerializer(read_only=True, many=True)
#     teachers = TeacherProfileSerializer(many=True, read_only=True)
#     students = StudentClassmatesSerializer(read_only=True, many=True)
#     class Meta:
#         model = Class
#         fields=['id',"name", 'subjects', 'teachers', 'students', 'created_at']

# class MarkSerializer(ModelSerializer):
#     subject = SubjectSerializer(read_only=True)
#     # teacher_name = serializers.CharField(source='teacher.name', read_only=True)
#     # class_name = serializers.CharField(source='class_instance.name', read_only=True)

#     class Meta:
#         model = Mark
#         fields = [
#             'id',
#             'subject',
#             'homework_score',
#             'classwork_score',
#             'is_present',
#             'marked_at'
#         ]


# second version
from rest_framework import serializers
class StudentSubjectSerializer(ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name']

class StudentClassSerializer(ModelSerializer):
    class Meta:
        model = Class
        fields = ['id', 'name']

class ThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Theme
        fields = ['id', 'name', 'created_at']

class SubjectSerializer(serializers.ModelSerializer):
    themes = serializers.SerializerMethodField()
    
    def get_themes(self, subject):
        # Get the current class from the context
        current_class = self.context.get('current_class')
        if current_class:
            # Filter themes by both subject and class
            themes = Theme.objects.filter(
                subject=subject,
                class_name=current_class
            )
            return ThemeSerializer(themes, many=True).data
        return []

    class Meta:
        model = Subject
        fields = ['id', 'name', 'themes']

class StudentDetailSerilizer(ModelSerializer):
    current_class = StudentClassSerializer(read_only=True)
    subjects = serializers.SerializerMethodField()

    def get_subjects(self, obj):
        subjects = obj.current_class.subjects.all()
        # Pass the current_class in the context
        serializer = SubjectSerializer(
            set(subjects), 
            many=True,
            context={'current_class': obj.current_class}
        )
        return serializer.data
    
    class Meta:
        model = Student
        fields = ['id', 'first_name', 'last_name', 'subjects',
                  'gender', 'current_class', 'mobile_number']
        
        
from rest_framework import serializers
from test_olish.models import TestSession

class TestHistorySerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(source='created_at')
    totalQuestions = serializers.SerializerMethodField()
    unanswered = serializers.SerializerMethodField()
    result = serializers.FloatField(source='test_result.total_score')
    passed = serializers.BooleanField(source='test_result.passed')

    class Meta:
        model = TestSession
        fields = ['id', 'date', 'totalQuestions', 'unanswered', 'passed', 'result']

    def get_totalQuestions(self, obj):
        return len(obj.selected_question_ids)

    def get_unanswered(self, obj):
        answered_count = obj.testresult.student_answers.count()
        total_questions = len(obj.selected_question_ids)
        return total_questions - answered_count