# from corecode.models import Class, Subject
from .models import User
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import transaction
# from staffs.models import Teacher
from rest_framework.serializers import ModelSerializer, Serializer

# class SubjectSerializer(ModelSerializer):

#     class Meta:
#         model = Subject
#         fields = '__all__'

# class ClassSerializer(ModelSerializer):

#     class Meta:
#         model = Class
#         fields = ('class_name',)

# class UserSerializer(ModelSerializer):

#     class Meta:
#         model = User
#         fields = ('username',)

# class TeacherSerializer(ModelSerializer):

#     user = UserSerializer(read_only=True)
#     class_name = ClassSerializer(read_only=True)
#     subject = SubjectSerializer(read_only=True)

#     class Meta:
#         model = Teacher
#         fields = ('id', 'user', 'first_name', 'last_name', 
#                   'phone_number', 'class_name','subject', 'created_at')
# # class Teacher(models.Model):

# #     user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
# #     first_name = models.CharField(max_length=50)
# #     last_name = models.CharField(max_length=50)
# #     phone_number = models.PositiveIntegerField(blank=True, null=True)

# #     class_name = models.ManyToManyField(Class)
# #     subject = models.ManyToManyField(Subject)
# #     created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    
# #     def __str__(self):

# #         return self.user + " " +  self.subject

class RegisterUserSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = ('email', 'username', 'password')
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        email = validated_data.pop('email', None)
        with transaction.atomic():
            # user = super().create(validated_data)
            user = self.Meta.model(**validated_data)

            user.email = email.lower()
            
            if password is not None:
                user.set_password(password)

            user.save()
            return user