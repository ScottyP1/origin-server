from django.db import models
from django.contrib.auth.models import AbstractUser

class Client(AbstractUser):
    email = models.EmailField(unique=True)

    username = models.CharField(max_length=150, blank=True, null=True, unique=False)

    avatar_url = models.URLField(max_length=500, blank=True, null=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    followers = models.IntegerField(default=0)
    following = models.IntegerField(default=0)
    total_repos = models.IntegerField(default=0)
    github_url = models.CharField(null=True, blank=True)
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [] 
