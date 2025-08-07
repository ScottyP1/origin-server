from django.db import models
from django.conf import settings

# Create your models here.
class RepoActivity(models.Model):
    client = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='repo_activities', on_delete=models.CASCADE)
    repo = models.ForeignKey("repo.Repo", related_name="repo_activities", on_delete=models.CASCADE)
    type = models.CharField(max_length=100)
    author = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField()
    github_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    