from rest_framework import serializers
from django.contrib.auth import get_user_model
from repo.serializers import RepoSerializer
from repoActivity.serializers import RepoActivitySerializer

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email", "password", "username")

    def create(self, validated_data):
        return User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            username=validated_data["email"],
        )


class UserSerializer(serializers.ModelSerializer):
    tracked_repos = RepoSerializer(many=True, read_only=True)
    activity = RepoActivitySerializer(many=True, read_only=True)
    total_open_prs = serializers.SerializerMethodField()
    total_open_issues = serializers.SerializerMethodField()
    total_commits = serializers.SerializerMethodField()
    github_connected = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id","username","email",'github_url',
            "avatar_url","full_name","followers","following",
            "tracked_repos","total_open_prs","total_open_issues","total_commits",
            "activity","total_repos","github_connected"
        ]

    def get_total_open_prs(self, obj):
        return sum(r.open_pr_count for r in obj.tracked_repos.all())

    def get_total_open_issues(self, obj):
        return sum(r.open_issue_count for r in obj.tracked_repos.all())

    def get_total_commits(self, obj):
        return sum(r.commit_count for r in obj.tracked_repos.all())

    def get_github_connected(self, obj):
        return obj.social_accounts.filter(provider="github").exists()