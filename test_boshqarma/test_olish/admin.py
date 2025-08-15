from django.contrib import admin
from .models import TestResult, TestSession, Question, Option, StudentAnswer
# Register your models here.

admin.site.register(TestSession)
admin.site.register(TestResult)
admin.site.register(Question)
admin.site.register(Option)
admin.site.register(StudentAnswer)