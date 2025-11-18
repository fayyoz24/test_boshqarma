from .models import Class, Subject, Mark
from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework import serializers
from staffs.models import Teacher
from students.models import Student
from myclick.models import UserSessionAccess
from rest_framework import serializers
from .models import MonthSession, Theme

class ClassAdminSerializer(ModelSerializer):
    class Meta:
        model = Class
        fields=['id', 'name']


class SubjectAdminSerializer(ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name']

    def update(self, instance, validated_data):
        # Update subject name
        instance.name = validated_data.get('name', instance.name)
        instance.save()

        return instance

class MarkSerializer(ModelSerializer):
    subject = SubjectAdminSerializer(read_only=True)
    # teacher_name = serializers.CharField(source='teacher.name', read_only=True)
    # class_name = serializers.CharField(source='class_instance.name', read_only=True)

    class Meta:
        model = Mark
        fields = [
            'id',
            'subject',
            'homework_score',
            'classwork_score',
            'is_present',
            'marked_at'
        ]


class TeacherAdminProfileSerializer(serializers.ModelSerializer):
    subject = SubjectAdminSerializer(read_only = True)
    teaching_classes = ClassAdminSerializer(many=True, read_only=True)  # Using the related_name from Class model
    class Meta:
        model = Teacher
        fields=['id', 'first_name', 'last_name', 'phone_number', 'subject', 'created_at', 'teaching_classes']


class StudentClassmatesAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'first_name', 'last_name', 'gender', 'parent_mobile_number', 'address', "current_status"]


class ClassDetailSerializer(serializers.ModelSerializer):
    subjects = SubjectAdminSerializer(read_only=True, many=True)
    teachers = TeacherAdminProfileSerializer(read_only=True, many=True)
    students = StudentClassmatesAdminSerializer(read_only=True, many=True)

    class Meta:
        model = Class
        fields = ['id', 'name', 'subjects', 'teachers', 'students', 'created_at']

class ClassUpdateSerializer(serializers.ModelSerializer):
    subjects = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all(), many=True)
    teachers = serializers.PrimaryKeyRelatedField(queryset=Teacher.objects.all(), many=True)
    students = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all(), many=True)

    class Meta:
        model = Class
        fields = ['id', 'name', 'subjects', 'teachers', 'students', 'created_at']

    def update(self, instance, validated_data):
        # Update subjects
        subjects = validated_data.pop('subjects', [])
        instance.subjects.set(subjects)  # Replaces the old subjects

        # Update teachers
        teachers = validated_data.pop('teachers', [])
        instance.teachers.set(teachers)  # Replaces the old teachers

        # Update students
        students = validated_data.pop('students', [])
        instance.students.set(students)  # Replaces the old students

        # Update the rest of the fields (like name)
        instance.name = validated_data.get('name', instance.name)
        instance.save()

        return instance
    

# StudentAdminSerializer()
class StudentAdminSerializer(serializers.ModelSerializer):

    class Meta:
        model = Student
        fields = ['id', 'first_name', 'last_name', 'mobile_number']

class ClassTeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields=['id', 'first_name', 'last_name']

# second version
class ClassDetailSerializer(serializers.ModelSerializer):
    subjects = SubjectAdminSerializer(read_only=True, many=True)
    teachers = ClassTeacherSerializer(read_only=True, many=True)

    class Meta:
        model = Class
        fields = ['id', 'name', 'subjects', 'teachers', 'created_at']


from test_olish.serializers import SubjectSerializer
class ThemeSerializer(serializers.ModelSerializer):
    """
    Serializer for Themes
    """
    subject = SubjectSerializer(read_only=True)
    
    class Meta:
        model = Theme
        fields = [
            'id', 
            'name', 
            'subject', 
            'timer', 
            'num_questions',
            'related_topics'
        ]


class MonthSessionSerializer(serializers.ModelSerializer):
    """
    Serializer for Sessions with nested Themes
    """
    is_paid = serializers.SerializerMethodField()
    # themes = ThemeSerializer(many=True, read_only=True)
    
    class Meta:
        model = MonthSession
        fields = [
            'id', 
            'name', 
            # 'description', 
            'price', 
            'is_paid', 
            # 'themes',
            'created_at'
        ]
    
    def get_is_paid(self, obj):
        """
        Check if the current user has paid for this session
        """
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
        
        return UserSessionAccess.objects.filter(
            user=user, 
            session=obj
        ).exists()
    
class MonthSessionGetSerializer(serializers.ModelSerializer):
    """
    Serializer for Sessions with nested Themes
    """
    # is_paid = serializers.SerializerMethodField()
    themes = ThemeSerializer(many=True, read_only=True)
    
    class Meta:
        model = MonthSession
        fields = [
            'id', 
            'name', 
            # 'description', 
            'price', 
            # 'is_paid', 
            'themes',
            'created_at'
        ]


class MonthSessionSerializer(serializers.ModelSerializer):
    themes = serializers.SerializerMethodField()
    is_paid = serializers.SerializerMethodField()
    
    class Meta:
        model = MonthSession
        fields = ['id', 'name', 'description', 'price', 'is_paid', 'themes', 'created_at']
    
    def get_themes(self, obj):
        # Get student from context
        student = self.context.get('student')
        student_class = student.current_class
        
        # Filter themes that are applicable to the student's class
        themes = obj.themes.filter(class_name=student_class)
        return ThemeSerializer(themes, many=True).data
    
    def get_is_paid(self, obj):
        # Check if hasattr to handle the case where we manually added is_paid
        if hasattr(obj, 'is_paid'):
            return obj.is_paid
        
        # Otherwise check database
        user = self.context['request'].user
        return UserSessionAccess.objects.filter(
            user=user,
            session=obj
        ).exists()


class SubjectSerializer(serializers.ModelSerializer):
    themes = serializers.SerializerMethodField()
    
    def get_themes(self, subject):
        # Get the current class from the context
        current_class = self.context.get('current_class')
        if current_class:
            # Filter themes by both subject and class
            themes = Theme.objects.filter(
                subject=subject,
                class_name=current_class
            )
            return ThemeSerializer(themes, many=True).data
        return []

    class Meta:
        model = Subject
        fields = ['id', 'name', 'themes']

# class StudentDetailSerilizer(ModelSerializer):
#     current_class = StudentClassSerializer(read_only=True)
#     subjects = serializers.SerializerMethodField()

#     def get_subjects(self, obj):
#         subjects = obj.current_class.subjects.all()
#         # Pass the current_class in the context
#         serializer = SubjectSerializer(
#             set(subjects), 
#             many=True,
#             context={'current_class': obj.current_class}
#         )
#         return serializer.data
    
#     class Meta:
#         model = Student
#         fields = ['id', 'first_name', 'last_name', 'subjects',
#                   'gender', 'current_class', 'mobile_number']

