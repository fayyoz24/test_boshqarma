from rest_framework import serializers
from .models import Option, Question, TestResult, TestSession, StudentAnswer
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count, F
from django.shortcuts import get_object_or_404
from corecode.models import Theme

class QuestionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields ="__all__"
        
    def create(self, validated_data):
        """
        Custom create method to handle theme association
        """
        # Get theme from context
        theme = self.context.get('theme')
        
        # Create question with theme
        if theme:
            validated_data['theme'] = theme
        
        return super().create(validated_data)


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['id', 'title', 'image']

class QuestionSerializer(serializers.ModelSerializer):
    options = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ['id', 'title', 'image', 'options']

    def get_options(self, obj):
        """
        Returns shuffled options for the question
        """
        shuffled_options = obj.get_shuffled_options()
        return OptionSerializer(shuffled_options, many=True).data


class ThemeQuestionTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Theme
        fields = ['id', 'name', 'num_questions', 'timer']


class TestSessionSerializer(serializers.ModelSerializer):
    questions = serializers.SerializerMethodField()
    theme = ThemeQuestionTestSerializer()

    class Meta:
        model = TestSession
        fields = ['id', 'theme','is_completed', 'created_at', 'questions']

    def get_questions(self, obj):
        """
        Retrieve and shuffle questions for this test session
        """
        questions = Question.objects.filter(id__in=obj.selected_question_ids)
        return QuestionSerializer(questions, many=True).data
    

class StudentAnswerSerializer(serializers.ModelSerializer):
    question_id = serializers.IntegerField()
    selected_option_id = serializers.IntegerField()

    class Meta:
        model = StudentAnswer
        fields = ['question_id', 'selected_option_id']

    def validate(self, data):
        """
        Validate that question and selected option exist and are related
        """
        try:
            question = Question.objects.get(id=data['question_id'])
            option = Option.objects.get(id=data['selected_option_id'])
            
            if option.question_id != question.id:
                raise serializers.ValidationError(
                    "Selected option does not belong to the specified question"
                )
            
            # Add validated objects to the data
            data['question'] = question
            data['selected_option'] = option
            
            return data
        except Question.DoesNotExist:
            raise serializers.ValidationError("Question not found")
        except Option.DoesNotExist:
            raise serializers.ValidationError("Option not found")

class TestSubmissionSerializer(serializers.Serializer):
    answers = StudentAnswerSerializer(many=True)

    def validate_answers(self, value):
        if not value:
            raise serializers.ValidationError("At least one answer must be provided")
        return value

class TestResultOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestResult
        fields = ['total_score', 'passed', 'created_at']

class AnswerSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    selected_option_id = serializers.IntegerField(required=False, allow_null=True)

class AnswersListSerializer(serializers.Serializer):
    answers = AnswerSerializer(many=True)







class ThemeTestHistorySerializer(serializers.ModelSerializer):
    passed = serializers.SerializerMethodField()
    total_questions = serializers.SerializerMethodField()
    correct_answers = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    score = serializers.SerializerMethodField()
    topics = serializers.SerializerMethodField()

    class Meta:
        model = Theme
        fields = ['id', 'name', 'passed', 'total_questions', 'correct_answers', 'created_at', 'score', 'topics']
    
    def get_passed(self, obj):
        test_session = obj.testsession_set.filter(
            user=self.context['request'].user,
            is_completed=True
        ).select_related('testresult').first()
        return test_session.testresult.passed if test_session and hasattr(test_session, 'testresult') else False
    
    def get_total_questions(self, obj):
        test_session = obj.testsession_set.filter(
            user=self.context['request'].user,
            is_completed=True
        ).first()
        return len(test_session.selected_question_ids) if test_session else 0
    
    def get_score(self, obj):
        test_session = obj.testsession_set.filter(
            user=self.context['request'].user,
            is_completed=True
        ).first()

        return test_session.testresult.total_score

    
    def get_correct_answers(self, obj):
        test_session = obj.testsession_set.filter(
            user=self.context['request'].user,
            is_completed=True
        ).select_related('testresult').first()
        if test_session and hasattr(test_session, 'testresult'):
            return test_session.testresult.student_answers.filter(is_correct=True).count()
        return 0
    
    def get_created_at(self, obj):
        test_session = obj.testsession_set.filter(
            user=self.context['request'].user,
            is_completed=True
        ).first()
        return test_session.created_at if test_session else None
    
    def get_topics(self, obj):
        return obj.related_topics.split(",")
    

class ClassTestResultsBySubjectThemeSerializer(serializers.Serializer):
    theme_name = serializers.CharField()
    average_score = serializers.FloatField()
    total_tested_students = serializers.IntegerField()
    passing_students = serializers.IntegerField()
    class_name = serializers.CharField()
    subject_name = serializers.CharField()


class StudentThemeResultSerializer(serializers.Serializer):
    student_name = serializers.CharField()
    test_score = serializers.FloatField()
    correct_answers = serializers.IntegerField()
    status = serializers.BooleanField()  # Change to BooleanField since it comes from test_result.passed
    topics_to_improve = serializers.CharField()
    completed_at = serializers.DateTimeField()

from corecode.models import Subject
class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name']  # Add any other subject fields you need

class SchoolSubjectAverageSerializer(serializers.Serializer):
    subject = SubjectSerializer()  # Changed from subject_name to full subject
    average_results = serializers.FloatField()