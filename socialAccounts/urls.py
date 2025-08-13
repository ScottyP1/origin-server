from django.urls import path
from .views import GitHubConnectView

urlpatterns = [
    path("github/connect/", GitHubConnectView.as_view(), name='github-connect'),
]
