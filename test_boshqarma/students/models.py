from django.db import models
from users.models import User
from corecode.models import Class
from django.core.validators import RegexValidator
from time import timezone
# Create your models here.

class Student(models.Model):
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    first_name = models.CharField(
        max_length=100, verbose_name="First Name")
    last_name = models.CharField(
        max_length=100, verbose_name="Last Name")
    other_name = models.CharField(
        max_length=100, verbose_name="Other Name", blank=True, null=True)

    # The first option is kept empty, to show the corresponding text as
    # the first option in the dropdown
    GENDER_CHOICES = [('', 'Select'), ('F', 'Female'),
                      ('M', 'Male'), ('O', 'Other')]    
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)

    # Using verbose_name in the form.
    # prof_pic = models.ImageField(default=user_default_pro_pic,
    #                             upload_to=user_dir,
    #                             verbose_name="Profile Picture",
    #                             validators=[file_size], null=True, blank=True)
    STATUS_CHOICES = [("active", "Active"), ("inactive", "Inactive")]

    # current_status = models.CharField(
    #     max_length=10, choices=STATUS_CHOICES, default="active"
    # )
    # date_of_birth = models.DateField(auto_now_add=True)
    current_class = models.ForeignKey(
        Class, on_delete=models.SET_NULL, blank=True, null=True
    )
    date_of_admission = models.DateField(auto_now_add=True)
    date_of_leaving = models.DateField(null=True, blank=True)
    mobile_num_regex = RegexValidator(
        regex="^[0-9]{10,15}$", message="Entered mobile number isn't in a right format!"
    )
    parent_mobile_number = models.CharField(
        validators=[mobile_num_regex], max_length=13, blank=True, null=True
    )
    mobile_number = models.CharField(
        validators=[mobile_num_regex], max_length=13, blank=True, null=True
        )
    address = models.TextField(blank=True, null=True)
    others = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.first_name}"
