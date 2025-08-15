from .models import Class, Subject, MonthSession
from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework import serializers
from students.models import Student
from myclick.models import UserSessionAccess
from rest_framework import serializers


class MonthSessionSerializer(serializers.ModelSerializer):
    """
    Serializer for MonthSessions with subjects
    """
    is_paid = serializers.SerializerMethodField()
    subjects = serializers.SerializerMethodField()
    
    class Meta:
        model = MonthSession
        fields = [
            'id', 
            'name', 
            'description', 
            'price', 
            'is_paid', 
            'subjects', 
            'created_at'
        ]
    
    def get_subjects(self, obj):
        """
        Get subjects for the current student's class
        """
        # Get student from context
        student = self.context.get('student')
        
        # If no student context, return all subjects for this MonthSession
        if not student or not student.current_class:
            return SubjectSerializer(obj.subjects.all(), many=True).data
        
        # Filter subjects that match the student's class subjects
        student_class_subjects = student.current_class.subjects.all()
        matching_subjects = obj.subjects.filter(id__in=student_class_subjects.values_list('id', flat=True))
        
        return SubjectSerializer(matching_subjects, many=True).data
    
    def get_is_paid(self, obj):
        """
        Check if the current user has paid for this session
        """
        # Check if manually added is_paid attribute exists
        if hasattr(obj, 'is_paid'):
            return obj.is_paid
        
        # Otherwise check database
        user = self.context['request'].user
        return UserSessionAccess.objects.filter(
            user=user,
            session=obj
        ).exists()

class SubjectSerializer(serializers.ModelSerializer):
    """
    Simple serializer for Subject
    """
    class Meta:
        model = Subject
        fields = ['id', 'name']

class MonthSessionGetSerializer(serializers.ModelSerializer):
    """
    Alternative serializer for MonthSessions
    """
    subjects = SubjectSerializer(many=True, read_only=True)
    
    class Meta:
        model = MonthSession
        fields = [
            'id', 
            'name', 
            'description', 
            'price', 
            'subjects',
            'created_at'
        ]
