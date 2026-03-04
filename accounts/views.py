from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from rest_framework import generics, status

def get_tokens_for_user(user):
    refresh=RefreshToken.for_user(user)
    return {
        'refresh':str(refresh),
        'access':str(refresh.access_token)
    }
    
class RegisterView(APIView):
    permission_classes=[AllowAny]
    
    
    def post(self,request):
        serializer=RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user=serializer.save()
            tokens=get_tokens_for_user(user)
            return Response({
                'message':"Registration successful.",
                'user': UserSerializer(user).data,
                'tokens':tokens
            },status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class LoginView(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        serializer=LoginSerializer(data=request.data)
        if serializer.is_valid():
            user=serializer.validated_data['user']
            tokens=get_tokens_for_user(user)
            return Response({
                'message':"Login successful.",
                'user': UserSerializer(user).data,
                'tokens':tokens
            },status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LogoutView(APIView):
    permission_classes=[IsAuthenticated]
    
    def post(self,request):
        try:
            refresh_token=request.data['refresh']
            token=RefreshToken(refresh_token)
            token.blacklist()
            return Response({
                'message':"Logout successful."
            },status=status.HTTP_200_OK)
        except Exception:
            return Response({
                'message':"Logout failed."
            },status=status.HTTP_400_BAD_REQUEST)
            
class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class=UserSerializer
    permission_classes=[IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    
    
class UserListView(generics.ListAPIView):
    serializer_class=UserSerializer
    permission_classes=[IsAuthenticated]


    def get_queryset(self):
        return User.objects.exclude(id=self.request.user.id)
    
    