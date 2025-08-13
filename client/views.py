import os
import random
import requests
from django.contrib.auth import get_user_model
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
import rest_framework.status as s
from rest_framework_simplejwt.tokens import RefreshToken
from decouple import config

from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer, RegisterSerializer

User = get_user_model()

MAILGUN_DOMAIN = config("MAILGUN_DOMAIN")
MAILGUN_API_KEY = config("MAILGUN_API_KEY")


class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=s.HTTP_200_OK)

    def put(self, request):
        client = request.user
        email = request.data.get("email", "").lower()
        try:
            EmailValidator()(email)
        except ValidationError:
            return Response({"error": "Invalid email address"}, status=s.HTTP_400_BAD_REQUEST)

        client.email = email
        client.save()
        return Response(status=s.HTTP_200_OK)

    def delete(self, request):
        request.user.delete()
        
        return Response(status=s.HTTP_204_NO_CONTENT)
    
class RemoveSocial(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        user.social_accounts.all().delete()

        user.tracked_repos.all().delete()

        user.github_connected = False
        user.username = ""
        user.github_url = ""
        user.avatar_url = None
        user.full_name = ""
        user.followers = 0
        user.following = 0
        user.total_commits = 0
        user.total_open_prs = 0
        user.total_open_issues = 0
        user.total_repos = 0
        user.save()

        return Response(UserSerializer(user).data, status=s.HTTP_200_OK)


class RegisterSendCode(APIView):
    def post(self, request):
        email = request.data.get("email", "").lower()

        # 1. Validate email format
        try:
            EmailValidator()(email)
        except ValidationError:
            return Response({"error": "Invalid email address"}, status=s.HTTP_400_BAD_REQUEST)

        # 2. Check if user already exists
        if User.objects.filter(email=email).exists():
            return Response({"error": "Email is already registered"}, status=s.HTTP_400_BAD_REQUEST)

        # 3. Generate and store code
        code = f"{random.randint(100000, 999999)}"
        cache.set(f"verify:{email}", code, timeout=600)  # store for 10 minutes

        # 4. Send email using Mailgun API
        try:
            response = requests.post(
                f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
                auth=("api", MAILGUN_API_KEY),
                data={
                    "from": f"No Reply <no-reply@{MAILGUN_DOMAIN}>",
                    "to": [email],
                    "subject": "Verify your account",
                    "text": f"Your verification code is: {code}\nThis code will expire in 10 minutes.",
                }
            )
            response.raise_for_status()
            
        except requests.RequestException as e:
            return Response({"error": f"Failed to send email: {str(e)}"}, status=s.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": "Verification code sent"}, status=s.HTTP_200_OK)


class RegisterVerifyCode(APIView):
    def post(self, request):
        email = request.data.get("email", "").lower()
        code = request.data.get("code")

        #Check code
        stored_code = cache.get(f"verify:{email}")
        if not stored_code or stored_code != code:
            return Response({"error": "Invalid or expired verification code"}, status=s.HTTP_400_BAD_REQUEST)

        # Clear verification code
        cache.delete(f"verify:{email}")

        return Response({"Verified" : True}, status=s.HTTP_200_OK)
        
        
class Register(APIView):
    def post(self, request):
        ser = RegisterSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = ser.save()

        refresh = RefreshToken.for_user(user)
        return Response({
            "user": UserSerializer(user).data,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }, status=s.HTTP_201_CREATED)
