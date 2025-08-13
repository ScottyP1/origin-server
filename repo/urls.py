from django.urls import path
from .views import getTrackedRepos, getAllRepos, AddRepoToUser

urlpatterns = [
    path('tracked/', getTrackedRepos.as_view(), name='user_repos'),
    path('tracked/<int:id>/', getTrackedRepos.as_view(), name='user_repo'),
    path("all/", getAllRepos.as_view(), name='all_user_repos'),
    path('add/', AddRepoToUser.as_view(), name='add_repo')
]
