from django.db import models
from corecode.models import Subject, Class, School,Tuman
from users.models import User
from django.db.models import Count, Avg, Q
from django.db.models.functions import Coalesce
# Create your models here.

class Teacher(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.PositiveIntegerField(blank=True, null=True)

    subject = models.ForeignKey(Subject, on_delete=models.DO_NOTHING, default=None)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    
    def __str__(self):

        return self.first_name + " " +  self.subject.name

class Director(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.PositiveIntegerField(blank=True, null=True)

    school = models.ForeignKey(School, on_delete=models.DO_NOTHING, default=None)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    
    def __str__(self):

        return self.first_name + " " +  self.school.name
    


class Kattakon(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.PositiveIntegerField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def get_analytics(self):
        """Get comprehensive analytics for all tumans"""
        tumans = Tuman.objects.annotate(
            # Count total students in the tuman
            student_count=Count(
                'school__class__student',  # Changed from current_class to student
                distinct=True
            ),
            # Count students who took tests
            tested_count=Count(
                'school__class__student__user__testsession',
                distinct=True
            ),
            # Count students who passed
            passed_count=Count(
                'school__class__student__user__testsession__testresult',
                filter=Q(
                    school__class__student__user__testsession__testresult__passed=True
                ),
                distinct=True
            ),
            # Calculate average score
            average_score=Coalesce(
                Avg(
                    'school__class__student__user__testsession__testresult__total_score'
                ),
                0.0
            )
        )

        # Calculate totals
        total_students = sum(tuman.student_count for tuman in tumans)
        total_tested = sum(tuman.tested_count for tuman in tumans)
        total_passed = sum(tuman.passed_count for tuman in tumans)

        # Calculate overall average score
        total_scores = sum(tuman.average_score * tuman.tested_count for tuman in tumans)
        average_score = round(total_scores / total_tested, 1) if total_tested > 0 else 0.0

        return {
            'tumans': tumans,
            'total_students': total_students,
            'total_tested': total_tested,
            'total_passed': total_passed,
            'average_score': average_score
        }
    def __str__(self):

        return self.first_name
    