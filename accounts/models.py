from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    bio=models.TextField(blank=True, null=True)
    avatar=models.ImageField(upload_to='avatars/', blank=True,null=True)
    is_online=models.BooleanField(default=False)
    last_seen=models.DateTimeField(blank=True,null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.username 
