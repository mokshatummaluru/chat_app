from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    password=serializers.CharField(write_only=True, min_length=8)
    password2=serializers.CharField(write_only=True)
    
    class Meta:
        model=User
        fields=[
            'id','username','email','password','password2',
            'first_name','last_name',
        ]
        
    def validate(self,attrs):
        if(attrs['password']!=attrs['password2']):
            raise serializers.ValidationError({'password':"Passwords don't match"})
        return attrs
    
    def create(self,validated_data):
        validated_data.pop('password2')
        password=validated_data.pop('password')
        user=User(**validated_data)
        user.set_password(password)
        user.save()
        return user
    
    
class LoginSerializer(serializers.Serializer):
    username=serializers.CharField()
    password=serializers.CharField(write_only=True)
    
    def validate(self,attrs):
        username=attrs.get('username')
        password=attrs.get('password')
        
        user=authenticate(username=username,password=password)
        if not user:
            raise serializers.ValidationError("Invalid credentials")
        if not user.is_active:
            raise serializers.ValidationError("This account is disabled.")
        
        attrs['user']=user
        return attrs
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=[
            'id','username','email','first_name','last_name',
            'is_online','last_seen','created_at'
        ]
        
        read_only_fields=['id','is_online','last_seen','created_at']
        
    