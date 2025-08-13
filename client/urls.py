from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import UserDetailView, Register, RegisterSendCode, RegisterVerifyCode, RemoveSocial

urlpatterns = [
    path('user/', UserDetailView.as_view(), name='user-detail'),
    path('signup/', Register.as_view(), name='register-user'),
    path('send-code/', RegisterSendCode.as_view(), name='send-code'),
    path('verify-code/', RegisterVerifyCode.as_view(), name='verify-code'),
    path('unlink/', RemoveSocial.as_view(), name='remove-git'),
    # JWT auth
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

]


