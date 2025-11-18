from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
# from .functions import (
#     user_default_pro_pic, user_dir, file_size
# )
class User(AbstractUser):

    username = models.CharField(max_length=100, unique=True)
    # email = models.EmailField(null=True, blank=True)
    # first_name = models.CharField(
    #     max_length=100, verbose_name="First Name")
    # last_name = models.CharField(
    #     max_length=100, verbose_name="Last Name")

    # The first option is kept empty, to show the corresponding text as
    # the first option in the dropdown
    # GENDER_CHOICES = [('', 'Select'), ('F', 'Female'),
    #                   ('M', 'Male'), ('O', 'Other')]
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

    # Default user_type must be defined to enforce security
    user_type = models.CharField(max_length=2, choices=USER_TYPE_CHOICES,
                                 default=STUDENT, verbose_name="User Type")
    USERNAME_FIELD = 'username'
    # REQUIRED_FIELDS = ['username']
    # gender = models.CharField(max_length=1, choices=GENDER_CHOICES, )

    # # Using verbose_name in the form.
    # prof_pic = models.ImageField(default=user_default_pro_pic,
    #                             upload_to=user_dir,
    #                             verbose_name="Profile Picture",
    #                             validators=[file_size])