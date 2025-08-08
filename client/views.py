from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
import rest_framework.status as s
from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer, RegisterSerializer

User = get_user_model()

class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=s.HTTP_200_OK)


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