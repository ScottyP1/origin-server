from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Repo
from .serializers import RepoSerializer
import requests
import time


class getUserRepo(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        access_token = user.github_access
        if not access_token:
            return Response({"detail": "GitHub access token not found."}, status=400)

        github_response = requests.get(
            "https://api.github.com/user/repos",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        if github_response.status_code != 200:
            return Response({"detail": "Failed to fetch repos from GitHub."}, status=github_response.status_code)

        repos_data = github_response.json()

        tracked_urls = set(user.repos.values_list('url', flat=True))

        filtered_repos = [repo for repo in repos_data if repo["html_url"] not in tracked_urls]

        return Response(filtered_repos)


class AddRepoToUser(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        repo_data = request.data
        access_token = user.github_access

        if not access_token:
            return Response({"detail": "GitHub access token not found."}, status=400)

        owner = repo_data["owner"]["login"]
        repo_name = repo_data["name"]
        
        headers = {"Authorization": f"Bearer {access_token}"}

        # Fetch pull request count (open)
        pr_response = requests.get(
            f"https://api.github.com/search/issues?q=repo:{owner}/{repo_name}+type:pr+state:open",
            headers=headers
        )
        pr_count = pr_response.json().get("total_count", 0)

        # Fetch issue count (open, excluding PRs)
        issue_response = requests.get(
            f"https://api.github.com/search/issues?q=repo:{owner}/{repo_name}+type:issue+state:open",
            headers=headers
        )
        issue_count = issue_response.json().get("total_count", 0)

        # Fetch commit activity stats
        commit_activity_url = f"https://api.github.com/repos/{owner}/{repo_name}/stats/commit_activity"
        commit_response = requests.get(commit_activity_url, headers=headers)

        # retry_count = 0
        # while commit_response.status_code == 202 and retry_count < 3:
        #     time.sleep(1)
        #     commit_response = requests.get(commit_activity_url, headers=headers)
        #     retry_count += 1

        if commit_response.status_code == 200:
            commit_data = commit_response.json()
            commit_count = sum(week['total'] for week in commit_data)
        else:
            commit_count = 0

        # Save or update Repo model with additional info
        repo, created = Repo.objects.update_or_create(
            client=user,
            url=repo_data["html_url"],
            defaults={
                "name": repo_data["name"],
                "description": repo_data.get("description", ""),
                "open_pr_count": pr_count,
                "open_issue_count": issue_count,
                "commit_count": commit_count,
            },
        )
        serializer = RepoSerializer(repo)
        return Response(serializer.data, status=201 if created else 200)
