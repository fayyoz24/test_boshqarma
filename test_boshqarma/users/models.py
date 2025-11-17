from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
# from .functions import (
#     user_default_pro_pic, user_dir, file_size
# )
class User(AbstractUser):

    username = models.CharField(max_length=100, unique=True)

    HEAD_TEACHER = 'HT'
    STUDENT = 'ST'
    TEACHER = "TR"
    ADMIN = 'AD'
    HEAD_TEACHER = 'HD'
    KATTAKON = 'KT'

    USER_TYPE_CHOICES = [(STUDENT, 'Student'),
                         (TEACHER, 'Teacher'), (ADMIN, 'Admin'),
                        (HEAD_TEACHER, 'HeadTeacher'), 
                        (KATTAKON, 'kattakon'),]

    user_type = models.CharField(max_length=2, choices=USER_TYPE_CHOICES,
                                 default=STUDENT, verbose_name="User Type")
    USERNAME_FIELD = 'username'
