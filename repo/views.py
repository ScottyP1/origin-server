from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import rest_framework.status as s
from .models import Repo
from .serializers import RepoSerializer
import requests
from django.shortcuts import get_list_or_404

class getTrackedRepos(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        client = request.user        
        repos = Repo.objects.filter(client=client)
        
        return Response(RepoSerializer(repos, many=True).data, status=s.HTTP_200_OK)


class getAllRepos(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        client= request.user
        access_token = client.github_access
        
        headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/vnd.github+json"}
        github_res = requests.get("https://api.github.com/user/repos?type=owner&per_page=100&page=1", headers=headers)
        github_data = github_res.json()

        tracked_ids = Repo.objects.filter(client=client).values_list("github_id", flat=True)
        untracked = [repo for repo in github_data if repo["id"] not in tracked_ids]
        data = []
        for repo in untracked:
            data.append({
                "id": repo["id"], "name": repo["name"],
                "url": repo["html_url"]})
        return Response(data, status=s.HTTP_200_OK)


class AddRepoToUser(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        repo_data = request.data
        access_token = user.github_access
        
        repo_name = repo_data["name"]
        
        headers = {"Authorization": f"Bearer {access_token}"}

        # Fetch pull request count (open)
        pr_response = requests.get(
            f"https://api.github.com/search/issues?q=repo:{user.username}/{repo_name}+type:pr+state:open",
            headers=headers
        )
        pr_count = pr_response.json().get("total_count", 0)

        # Fetch issue count (open, excluding PRs)
        issue_response = requests.get(
            f"https://api.github.com/search/issues?q=repo:{user.username}/{repo_name}+type:issue+state:open",
            headers=headers
        )
        issue_count = issue_response.json().get("total_count", 0)

        # Fetch commit activity stats
        commit_activity_url = f"https://api.github.com/repos/{user.username}/{repo_name}/stats/commit_activity"
        commit_response = requests.get(commit_activity_url, headers=headers)

        commit_data = commit_response.json()
        commit_count = sum(week['total'] for week in commit_data)

        repo, created = Repo.objects.get_or_create(client=user, github_id=repo_data.get("id"))
        repo.name = repo_data.get("name", "")
        repo.open_pr_count = pr_count
        repo.open_issue_count = issue_count
        repo.commit_count = commit_count
        repo.url = repo_data.get("url", "")
        
        repo.save()
        return Response(RepoSerializer(repo).data, status=s.HTTP_200_OK)
