from django.db import models
from django.contrib.auth.models import AbstractUser

class Client(AbstractUser):
    github_access = models.CharField(max_length=255, blank=True, null=True)
    avatar_url = models.URLField(max_length=500, blank=True, null=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    followers = models.IntegerField(blank=True, null=True)
    following = models.IntegerField(blank=True, null=True)
    REQUIRED_FIELDS = []
