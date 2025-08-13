from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import RepoActivity
from .serializers import RepoActivitySerializer
import rest_framework.status as s
from repo.models import Repo    
import requests
from socialAccounts.models import SocialAccount

class RecentActivityView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        activities = RepoActivity.objects.filter(repo__client=request.user).order_by('-created_at')[:25]
        return Response(RepoActivitySerializer(activities, many=True).data, status=s.HTTP_200_OK)
    
    
class SyncAllTrackedReposView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        client = request.user
        account = SocialAccount.objects.filter(user=client, provider="github").first()
        if not account:
            return Response({"error": "No GitHub account connected"}, status=400)

        headers = {"Authorization": f"Bearer {account.access_token}", "Accept": "application/vnd.github+json"}
        repos = Repo.objects.filter(client=client)

        for repo in repos:
            meta = requests.get(f"https://api.github.com/repositories/{repo.github_id}", headers=headers).json()
            full_name = meta.get("full_name")
            if not full_name:
                continue

            response = requests.get(f"https://api.github.com/repos/{full_name}/events", headers=headers)
            for event in (response.json() or [])[:30]: 
                event_id = str(event.get("id"))
                activity, _ = RepoActivity.objects.get_or_create(event_id=event_id, repo=repo)
                activity.type = event.get("type", "")
                
                actor = event.get("actor") or {}
                activity.author = actor.get("login", "")
                activity.created_at = event.get("created_at", "")

                # Extra info for display
                if activity.type == "PushEvent":
                    commits = event.get("payload", {}).get("commits", [])
                    if commits:
                        activity.title = commits[0].get("message", "Push")
                        activity.url = commits[0].get("url", "")
                elif activity.type in ["PullRequestEvent", "IssuesEvent"]:
                    pr_or_issue = event.get("payload", {}).get("pull_request") or event.get("payload", {}).get("issue")
                    if pr_or_issue:
                        activity.title = pr_or_issue.get("title", "")
                        activity.url = pr_or_issue.get("html_url", "")

                activity.save()

        return Response({"success": True}, status=s.HTTP_200_OK)

