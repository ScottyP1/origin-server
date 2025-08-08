from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
import rest_framework.status as s
import requests
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer 

User = get_user_model()

class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=s.HTTP_200_OK)

class GitHubOAuthCallbackView(APIView):
    def post(self, request):
        code = request.data.get("code")

        # Exchange code for access token
        token_response = requests.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "code": code,
            },
        )
        
        token_json = token_response.json()
        access_token = token_json.get("access_token")
        
        headers = {"Authorization": f"Bearer {access_token}"}

        user_response = requests.get(
            "https://api.github.com/user",
            headers=headers)
        user_data = user_response.json()

        email_res = requests.get("https://api.github.com/user/emails",
        headers=headers)
        user_email = email_res.json()

        
        user, created = User.objects.get_or_create(username=user_data.get("login", ""))
        user.email = user_email[0].get('email')
        user.github_access = access_token
        user.avatar_url = user_data.get("avatar_url", "")
        user.full_name = user_data.get("name", "")
        user.followers = user_data.get("followers", 0)
        user.following = user_data.get("following", 0)
        user.total_repos = user_data.get("public_repos", 0)
        
        user.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        serializer = UserSerializer(user)
        return Response({"user": serializer.data,"refresh": str(refresh),"access": str(refresh.access_token)}, status=s.HTTP_201_CREATED)
