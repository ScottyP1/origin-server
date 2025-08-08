from django.db import models
from django.conf import settings

# Create your models here.
class RepoActivity(models.Model):
    repo = models.ForeignKey("repo.Repo", related_name="repo_activities", on_delete=models.CASCADE)
    type = models.CharField(max_length=100)
    author = models.CharField(max_length=255, blank=True, null=True)
    event_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(null=True, blank=True)
    