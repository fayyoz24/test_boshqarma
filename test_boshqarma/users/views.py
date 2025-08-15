from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterUserSerializer

# from django.shortcuts import render
# from rest_framework import generics
# from .serializers import TeacherSerializer
# from staffs.models import Teacher
# from rest_framework.permissions import IsAuthenticated

# Create your views here.


# class TeacherProfileView(generics.ListAPIView):
#     permission_classes = [IsAuthenticated]
#     serializer_class = TeacherSerializer  
#     queryset = Teacher.objects.all()  

#     def get_queryset(self):
#         # Filter the queryset to return only the profile of the authenticated user
#         return Teacher.objects.filter(user=self.request.user)

class RegisterUserView(APIView):
     permission_classes=[AllowAny]

     def post(self, request):
            reg_serializer=RegisterUserSerializer(data=request.data)
            if reg_serializer.is_valid():

                new_user=reg_serializer.save()
                if new_user:
                    refresh = RefreshToken.for_user(new_user)

                    return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                                    },status=201)
            return Response(reg_serializer.errors, status=400)