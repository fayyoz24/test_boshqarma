from django.db import models
from users.models import User
from corecode.models import Class
from django.core.validators import RegexValidator
from time import timezone
# Create your models here.

class Student(models.Model):
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(
        max_length=100, verbose_name="First Name")
    last_name = models.CharField(
        max_length=100, verbose_name="Last Name")
    other_name = models.CharField(
        max_length=100, verbose_name="Other Name", blank=True, null=True)

    current_class = models.ForeignKey(
        Class, on_delete=models.SET_NULL, blank=True, null=True
    )

    def __str__(self):
        return f"{self.first_name}"
