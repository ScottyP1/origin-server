# social/views.py

import requests
from django.conf import settings
from rest_framework import status as s
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django.contrib.auth import get_user_model
from client.serializers import UserSerializer  
from .models import SocialAccount           

User = get_user_model()


class GitHubConnectView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        code = request.data.get("code")
        
        # Exchange code for token        
        exchange = requests.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={
                    "client_id": settings.GITHUB_CLIENT_ID,
                    "client_secret": settings.GITHUB_CLIENT_SECRET,
                    "code": code,
                })
            
        tokenData = exchange.json()
        access_token = tokenData.get("access_token")
  
        headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}

        #Fetch GitHub profile
        github_user = requests.get("https://api.github.com/user", headers=headers)
        gh_data = github_user.json()


        gh_id = str(gh_data.get("id") or "")

        # Link to SocialAccount
        SocialAccount.objects.update_or_create(
            provider="github",
            provider_user_id=gh_id,
            defaults={"user": request.user, "access_token": access_token},
        )

        #Update user profile fields
        user = request.user
        
        gh_login = gh_data.get("login")
        if gh_login:
            user.username = gh_login
        user.github_url = gh_data.get("html_url", "")
        user.avatar_url = gh_data.get("avatar_url",user.avatar_url )
        user.full_name = gh_data.get("name", user.full_name)
        user.followers = gh_data.get("followers", 0) or 0
        user.following = gh_data.get("following", 0) or 0
        user.total_repos = gh_data.get("public_repos") or 0
        user.save()

        return Response(UserSerializer(user).data, status=s.HTTP_200_OK)


