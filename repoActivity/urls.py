from django.urls import path
from .views import RecentActivityView, SyncAllTrackedReposView

urlpatterns = [
    path('sync/', SyncAllTrackedReposView.as_view(), name='sync'),
    path('recent/', RecentActivityView.as_view(), name='recent_activity'),
    # path('recent/<int:id>/', RepoActivityView.as_view(), name='repo_activity')
]
