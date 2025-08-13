from rest_framework import serializers
from .models import RepoActivity
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta


class RepoActivitySerializer(serializers.ModelSerializer):
    repo_name = serializers.SerializerMethodField()
    time_ago = serializers.SerializerMethodField()
    repo_url = serializers.SerializerMethodField()

    class Meta:
        model = RepoActivity
        fields = [
            "type",   
            "repo_name",  
            "time_ago",
            "author" ,
            "repo_url"   
        ]

    def get_repo_name(self, obj):
        return obj.repo.name if obj.repo else ""

    def get_repo_url(self, obj):
        return obj.repo.html_url
    
    
    def get_time_ago(self, obj):
        now = datetime.now(timezone.utc)
        delta = relativedelta(now, obj.created_at)

        if delta.years:
            return f"{delta.years}y ago"
        elif delta.months:
            return f"{delta.months}mo ago"
        elif delta.days:
            return f"{delta.days}d ago"
        elif delta.hours:
            return f"{delta.hours}h ago"
        elif delta.minutes:
            return f"{delta.minutes}m ago"
        return "just now"
