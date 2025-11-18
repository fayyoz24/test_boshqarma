from django.db import models
from users.models import User
from corecode.models import Subject, Theme
import random


class Question(models.Model):
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE)
    title = models.TextField()
    image = models.ImageField(upload_to='images/questions', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_shuffled_options(self):
        """
        Return options in a random order
        """
        options = list(self.option_set.all())
        random.shuffle(options)
        return options
    def __str__(self):
        return self.theme.name + ' - ' + self.title[:50]
    
class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    title = models.TextField()
    image = models.ImageField(upload_to='images/options', null=True, blank=True)
    is_correct = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question.title[:10] + ' - ' + str(self.is_correct) + ' - ' + self.title[:10]

class TestSession(models.Model):
    """
    Represents a unique test session for a user
    """
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)
    
    # Store the randomly selected question IDs to ensure consistency
    selected_question_ids = models.JSONField()

    @classmethod
    def create_new_test_session(cls, user, theme):
        """
        Create a new test session with random questions
        """
        # Select random question IDs
        question_ids = list(theme.question_set.values_list('id', flat=True))
        random.shuffle(question_ids)
        num_questions = theme.num_questions  # Use the theme parameter, not cls.theme
        selected_ids = question_ids[:num_questions]

        # Create test session
        test_session = cls.objects.create(
            user=user,
            theme=theme,
            selected_question_ids=selected_ids,
            is_completed=False
        )
        return test_session

    def __str__(self):
        return self.user.student.first_name + ' - ' + self.theme.name

class TestResult(models.Model):
    """Stores the test results for each test session"""
    test_session = models.OneToOneField(TestSession, on_delete=models.CASCADE)
    total_score = models.FloatField()
    passed = models.BooleanField()
    completed_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_questions(self):
        return len(self.test_session.selected_question_ids)

    @property
    def correct_answers(self):
        return self.student_answers.filter(is_correct=True).count()

    def calculate_score(self):
        """
        Calculate score based on correct answers
        """
        correct_answers = self.correct_answers
        total_questions = self.total_questions
        self.total_score = round((correct_answers / total_questions) * 100, 1) if total_questions > 0 else 0
        self.passed = self.total_score >= 50  # Passing threshold
        self.save()

class StudentAnswer(models.Model):
    """Stores individual student answers for a test session"""
    test_result = models.ForeignKey(TestResult, on_delete=models.CASCADE, related_name='student_answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.ForeignKey(Option, on_delete=models.CASCADE, null=True, blank=True)
    is_correct = models.BooleanField()