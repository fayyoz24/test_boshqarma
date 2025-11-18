from django.db import models
from django.utils import timezone
import random
from users.models import User
# from students.models import Student
# Create your models here.

class Tuman(models.Model):
    name = models.CharField(max_length=150)

    def __str__(self):
        return self.name

class School(models.Model):
    tuman = models.ForeignKey(Tuman, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=150)

    def __str__(self):
        return self.tuman.name + " " + self.name

class Subject(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

from django.core.exceptions import ValidationError


class MonthSession(models.Model):
    """
    Represents a test session containing multiple themes.
    """
    name = models.CharField(max_length=200)
    themes = models.ManyToManyField('Theme', related_name='monthsessions')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} (${self.price})"



class Theme(models.Model):

    class_name = models.ManyToManyField("Class", blank=True)
    name = models.CharField(max_length=200)
    timer = models.IntegerField(default=1200)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    related_topics = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    num_questions = models.IntegerField(default=30)

    def get_random_test(self):
        num_questions = self.num_questions

        # Get all questions for this subject
        all_questions = list(self.question_set.all())

        # Shuffle and select 30 unique questions
        random.shuffle(all_questions)
        selected_questions = all_questions[:num_questions]

        return selected_questions

    def __str__(self):
        return self.subject.name + " " + self.name


class Class(models.Model):

    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    subjects = models.ManyToManyField(Subject, blank=True)
    teachers = models.ManyToManyField("staffs.Teacher", related_name="teaching_classes")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        school_name = self.school.name if self.school else "No School"
        tuman_name = self.school.tuman.name if self.school and self.school.tuman else "No Tuman"
        return f"{self.name} {school_name} {tuman_name}"

    class Meta:
        verbose_name_plural = "Classes"


class Mark(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT, related_name="marks")
    teacher = models.ForeignKey("staffs.Teacher", on_delete=models.CASCADE, related_name="given_marks")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="received_marks")
    class_instance = models.ForeignKey(Class, on_delete=models.DO_NOTHING)
    is_present = models.BooleanField(default=True)  # Changed from absent to is_present for clarity
    homework_score = models.PositiveIntegerField(default=0)
    classwork_score = models.PositiveIntegerField(default=0)  # Changed from in_lesson for clarity

    marked_at = models.DateField(default=timezone.now)
    updated_at = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.student} - {self.subject} - {self.marked_at}"

    class Meta:
        ordering = ['-marked_at']
