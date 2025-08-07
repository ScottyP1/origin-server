from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import GitHubOAuthCallbackView, UserDetailView

urlpatterns = [
    path('user/', UserDetailView.as_view(), name='user-detail'),

    # JWT auth
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # path('github/', GitHubLogin.as_view(), name='github_login'),
    path('github/', GitHubOAuthCallbackView.as_view(), name='github_callback')
]


