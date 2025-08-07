from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer 

User = get_user_model()

class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

class GitHubOAuthCallbackView(APIView):
    def post(self, request):
        code = request.data.get("code")
        if not code:
            return Response({"detail": "Code not provided"}, status=status.HTTP_400_BAD_REQUEST)

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
        if not access_token:
            return Response({"detail": "Failed to get access token from GitHub", "error": token_json}, status=status.HTTP_400_BAD_REQUEST)

        # Get user basic info
        user_response = requests.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        user_data = user_response.json()

        if user_response.status_code != 200 or "login" not in user_data:
            return Response({"detail": "Failed to fetch user data from GitHub", "error": user_data}, status=status.HTTP_400_BAD_REQUEST)

        # Try to get public email, else fetch verified emails
        email = user_data.get("email")
        if not email:
            emails_res = requests.get(
                "https://api.github.com/user/emails",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            emails = emails_res.json()
            for e in emails:
                if e.get("primary") and e.get("verified"):
                    email = e.get("email")
                    break

        # Find or create user, and update extra fields
        user, created = User.objects.get_or_create(username=user_data["login"])
        user.email = email or ""
        user.github_access = access_token
        user.avatar_url = user_data.get("avatar_url", "")
        user.full_name = user_data.get("name", "")
        user.followers = user_data.get("followers", "")
        user.following = user_data.get("following", "")
        user.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        return Response({
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "avatar_url": user.avatar_url ,
                "full_name": user.full_name,
                'followers': user.followers,
                "following":user.following
            },
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        })