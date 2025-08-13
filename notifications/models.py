from django.db import models

# Create your models here.

class Notifications(models.Model):
    repo = models.ForeignKey('repo.Repo', related_name='notifications', on_delete=models.CASCADE)
    
    commits_sms = models.BooleanField(default=False)
    commits_email = models.BooleanField(default=False)
    
    prs_sms = models.BooleanField(default=False)
    prs_email = models.BooleanField(default=False)
    
    issues_sms = models.BooleanField(default=False)
    issues_email = models.BooleanField(default=False)
    
    reviews_sms = models.BooleanField(default=False)
    reviews_email = models.BooleanField(default=False)