from rest_framework import serializers
from django.contrib.auth import get_user_model
from repo.serializers import RepoSerializer
from repoActivity.serializers import RepoActivitySerializer

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    repos = RepoSerializer(many=True, read_only=True)
    activity = RepoActivitySerializer(many=True, read_only=True)
    total_open_prs = serializers.SerializerMethodField()
    total_open_issues = serializers.SerializerMethodField()
    total_commits = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'github_access',
            'avatar_url', 'full_name', 'followers', 'following',
            'repos', 'total_open_prs', 'total_open_issues', 'total_commits','activity'
        ]

    def get_total_open_prs(self, obj):
        repos = obj.repos.all()
        return sum(repo.open_pr_count for repo in repos)
        
    def get_total_open_issues(self, obj):
        repos = obj.repos.all()
        return sum(repo.open_issue_count for repo in repos)

    def get_total_commits(self, obj):
        repos = obj.repos.all()
        return sum(repo.commit_count for repo in repos)