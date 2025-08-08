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

        access_token = account.access_token
        
        headers = {"Authorization": f"Bearer {access_token}"}

        repos = Repo.objects.filter(client=client)

        for repo in repos:
            response = requests.get(f"https://api.github.com/repos/{client.username}/{repo.name}/events", headers=headers)

            for event in response.json()[:5]:   
                event_id = str(event.get("id")) 
                activity, created = RepoActivity.objects.get_or_create(event_id=event_id, repo=repo)                 
                activity.type = event.get("type", "")
                activity.author = event.get("actor").get("login", "")
                activity.created_at = event.get("created_at", "")
                activity.save()
        return Response({"success": True}, status=s.HTTP_200_OK)
