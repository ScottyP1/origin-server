from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import UserDetailView, Register

urlpatterns = [
    path('user/', UserDetailView.as_view(), name='user-detail'),
    path('signup/', Register.as_view(), name='register-user'),
    
    # JWT auth
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

]


