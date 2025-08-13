from django.db import models
from django.conf import settings

class SocialAccount(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="social_accounts",
    )
    provider = models.CharField(max_length=50)
    provider_user_id = models.CharField(max_length=255, unique=True, db_index=True)
    access_token = models.TextField(blank=True, default="")

