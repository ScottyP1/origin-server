from rest_framework import serializers
from .models import Repo
from repoActivity.serializers import RepoActivitySerializer
from notifications.serializers import NotificationsSerializer

class RepoSerializer(serializers.ModelSerializer):
    repo_activities = RepoActivitySerializer(many=True, read_only=True)
    notifications = NotificationsSerializer(many=True, read_only=True)
    
    class Meta:
        model = Repo
        fields = [
            'id',
            'name',
            'html_url',
            'open_pr_count',
            'open_issue_count',
            'commit_count',
            'repo_activities',
            'notifications'
        ]