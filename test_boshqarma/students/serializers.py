
from corecode.models import Subject, Class
from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework import serializers
from .models import Student
from rest_framework import serializers
from rest_framework import serializers
from test_olish.models import TestSession


class StudentSubjectSerializer(ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name']

class StudentClassSerializer(ModelSerializer):
    class Meta:
        model = Class
        fields = ['id', 'name']


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name']

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
        fields = ['id', 'first_name', 'last_name', 'subjects', 'current_class']

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