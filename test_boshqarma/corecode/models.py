from django.db import models
from django.utils import timezone
import random
from users.models import User
from django.core.exceptions import ValidationError

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

class MonthSession(models.Model):
    """
    Represents a test session containing multiple themes.
    """
    name = models.CharField(max_length=200)
    subjects = models.ManyToManyField(Subject, related_name='monthsessions')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} (${self.price})"


class Class(models.Model):

    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    subjects = models.ManyToManyField(Subject, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        school_name = self.school.name if self.school else "No School"
        tuman_name = self.school.tuman.name if self.school and self.school.tuman else "No Tuman"
        return f"{self.name} {school_name} {tuman_name}"

    class Meta:
        verbose_name_plural = "Classes"
