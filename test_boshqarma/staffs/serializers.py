from .models import Teacher
from rest_framework import serializers
from corecode.serializers import SubjectAdminSerializer
from corecode.models import Class, Mark, Theme
from students.models import Student

class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = ['id', 'name', 'created_at']


class ThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Theme
        fields = ['id', 'name', 'subject', 'related_topics', 'created_at']

# Modify ClassSerializer to include themes
class ClassThemeSerializer(serializers.ModelSerializer):
    themes = serializers.SerializerMethodField()

    class Meta:
        model = Class
        fields = ['id', 'name', 'themes']  # Add other fields you need

    def get_themes(self, obj):
        # Get themes specific to this class and the teacher's subject
        themes = Theme.objects.filter(
            class_name=obj,
            subject=self.context.get('teacher_subject')
        )
        return ThemeSerializer(themes, many=True).data

# TeacherProfileSerializer stays mostly the same but passes context
class TeacherProfileSerializer(serializers.ModelSerializer):
    subject = SubjectAdminSerializer(read_only=True)
    teaching_classes = ClassThemeSerializer(many=True, read_only=True)

    class Meta:
        model = Teacher
        fields = ['id', 'first_name', 'last_name', 'phone_number', 
                 'subject', 'created_at', 'teaching_classes']

    def to_representation(self, instance):
        # Pass the teacher's subject to ClassSerializer context
        self.context['teacher_subject'] = instance.subject
        return super().to_representation(instance)



# class TeacherProfileSerializer(serializers.ModelSerializer):
#     subject = SubjectAdminSerializer(read_only = True)
#     teaching_classes = ClassSerializer(many=True, read_only=True)  # Using the related_name from Class model
#     class Meta:
#         model = Teacher
#         fields=['id', 'first_name', 'last_name', 'phone_number', 'subject', 'created_at', 'teaching_classes']

class MarkEntrySerializer(serializers.ModelSerializer):
    student_id = serializers.IntegerField()
    is_present = serializers.BooleanField(default=True)
    homework_score = serializers.IntegerField(min_value=0)
    classwork_score = serializers.IntegerField(min_value=0)
    
    class Meta:
        model = Mark
        fields = ['student_id', 'is_present', 'homework_score', 'classwork_score']

class TeacherMarkClassSerializer(serializers.Serializer):
    subject_id = serializers.IntegerField()
    class_id = serializers.IntegerField()
    marks_list = MarkEntrySerializer(many=True)

    marked_at = serializers.DateField(
        required=True,
        format="%Y-%m-%d",  # Specify expected format
        input_formats=["%Y-%m-%d", "iso-8601"],  # Allow multiple formats
        error_messages={
            'invalid': 'Please provide the date in YYYY-MM-DD'
    }
        )


    def validate(self, data):
        request = self.context['request']
        print(request.user.user_type)
        if not hasattr(request.user, 'teacher'):
            raise serializers.ValidationError("User is not associated with a teacher profile")

        teacher = request.user.teacher
        
        # Validate if the teacher teaches this subject
        if teacher.subject.id != data['subject_id']:
            raise serializers.ValidationError("You don't teach this subject")

        # Validate if all students exist and are in the teacher's classes
        student_ids = [mark['student_id'] for mark in data['marks_list']]
        
        # Get all valid students (must be of type STUDENT and in teacher's classes)
        valid_students = Student.objects.filter(
            # user__user_type=User.STUDENT,
            enrolled_classes__teachers=teacher,
            id__in=student_ids
        ).values_list('id', flat=True)

        invalid_students = set(student_ids) - set(valid_students)
        if invalid_students:
            raise serializers.ValidationError(
                f"Invalid student IDs: {invalid_students}. Make sure all students exist, "
                "are of type STUDENT, and are in your classes"
            )
        
        return data

class MarkGetSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    class_name = serializers.CharField(source='class_instance.name', read_only=True)

    class Meta:
        model = Mark
        fields = ['id', 'student_name', 'subject_name', 'class_name', 'is_present', 
                  'homework_score', 'classwork_score', 'marked_at']
        










# serializers.py
from corecode.models import Tuman
from test_olish.models import TestSession, TestResult
from .models import Kattakon

class TumanAnalyticsSerializer(serializers.ModelSerializer):
    student_count = serializers.IntegerField()
    tested_count = serializers.IntegerField()
    passed_count = serializers.IntegerField()
    average_score = serializers.FloatField()
    
    class Meta:
        model = Tuman
        fields = ['id', 'name', 'student_count', 'tested_count', 'passed_count', 'average_score']

class KattakonAnalyticsSerializer(serializers.Serializer):
    tumans = TumanAnalyticsSerializer(many=True)
    total_students = serializers.IntegerField()
    total_tested = serializers.IntegerField()
    total_passed = serializers.IntegerField()
    average_score = serializers.FloatField()
