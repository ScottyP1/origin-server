from django.db import models
from django.conf import settings

class Repo(models.Model):
    client = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='tracked_repos', on_delete=models.CASCADE)
    github_id = models.BigIntegerField()
    name = models.CharField(max_length=255)
    html_url = models.URLField(blank=True, null=True)
    open_pr_count = models.IntegerField(default=0)
    open_issue_count = models.IntegerField(default=0)
    commit_count = models.IntegerField(default=0)
    
    
    class Meta:
        unique_together = ('client', 'github_id')
    