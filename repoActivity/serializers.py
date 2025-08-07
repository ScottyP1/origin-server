from rest_framework import serializers
from .models import RepoActivity
from repo.models import Repo
from datetime import datetime, timezone
import ast
from dateutil.relativedelta import relativedelta

class RepoActivitySerializer(serializers.ModelSerializer):
    repo_name = serializers.SerializerMethodField()
    time_ago = serializers.SerializerMethodField()
    summary = serializers.SerializerMethodField()

    class Meta:
        model = RepoActivity
        fields = [
            "id", "type", "author", "repo", "repo_name", "description", "created_at", "time_ago", "summary"
        ]

    def get_repo_name(self, obj):
        return obj.repo.name

    def get_time_ago(self, obj):
        now = datetime.now(timezone.utc)
        delta = relativedelta(now, obj.created_at)
        if delta.years: return f"{delta.years}y ago"
        if delta.months: return f"{delta.months}mo ago"
        if delta.days: return f"{delta.days}d ago"
        if delta.hours: return f"{delta.hours}h ago"
        if delta.minutes: return f"{delta.minutes}m ago"
        return "just now"

    def get_summary(self, obj):
        if obj.type == "PushEvent":
            try:
                payload = ast.literal_eval(obj.description)
                commits = payload.get("commits", [])
                if commits:
                    commit_msg = commits[0].get("message", "Pushed")
                    return f'{obj.author} pushed to {obj.repo.name} — "{commit_msg}"'
                return f'{obj.author} pushed to {obj.repo.name}'
            except Exception as e:
                return f'{obj.author} pushed to {obj.repo.name}'
        return f'{obj.author} did {obj.type} on {obj.repo.name}'
