from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import rest_framework.status as s
from .models import Repo
from .serializers import RepoSerializer
import requests
from notifications.models import Notifications
from socialAccounts.models import SocialAccount
from django.shortcuts import get_object_or_404

class getTrackedRepos(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        client = request.user        
        repos = Repo.objects.filter(client=client)
        
        return Response(RepoSerializer(repos, many=True).data, status=s.HTTP_200_OK)

    def delete(self, request, id):
        repo = get_object_or_404(Repo, id=id, client=request.user)
        repo.delete()
        return Response(status=s.HTTP_204_NO_CONTENT)
        
        

class getAllRepos(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        client= request.user
        account = SocialAccount.objects.filter(user=request.user, provider="github").first()
        if not account:
            return Response({"error": "No GitHub account connected"}, status=400)

        access_token = account.access_token

                
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
        return Response(RepoSerializer(data, many=True).data, status=s.HTTP_200_OK)


class AddRepoToUser(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        repo_id = request.data.get("id")
        repo_name = request.data.get("name")

        account = SocialAccount.objects.filter(user=user, provider="github").first()
        if not account:
            return Response({"error": "No GitHub account connected"}, status=400)

        headers = {
            "Authorization": f"Bearer {account.access_token}",
            "Accept": "application/vnd.github+json",
        }

        repo_meta = requests.get(f"https://api.github.com/repositories/{repo_id}", headers=headers)
        
        if repo_meta.status_code == 404:
            return Response({"error": "Repo not found with this id"}, status=404)
        meta = repo_meta.json()
        full_name = meta.get("full_name") 
        html_url = meta.get("html_url", "")

        # Counts via Search API (use full_name)
        pr_q = f"is:open is:pr repo:{full_name}"
        issue_q = f"is:open is:issue repo:{full_name}"
        pr_count = requests.get(f"https://api.github.com/search/issues?q={pr_q}", headers=headers).json().get("total_count", 0)
        issue_count = requests.get(f"https://api.github.com/search/issues?q={issue_q}", headers=headers).json().get("total_count", 0)

        # Commit activity 
        stats_url = f"https://api.github.com/repos/{full_name}/stats/commit_activity"

        r = requests.get(stats_url, headers=headers)
        commit_count = sum(week.get("total", 0) for week in r.json())

        repo, _ = Repo.objects.get_or_create(client=user, github_id=repo_id)
        repo.name = repo_name
        repo.html_url = html_url
        repo.open_pr_count = pr_count
        repo.open_issue_count = issue_count
        repo.commit_count = commit_count
        repo.save()

        return Response(RepoSerializer(repo).data, status=s.HTTP_200_OK)
