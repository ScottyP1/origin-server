from django.urls import path
from .views import getTrackedRepos, getAllRepos, AddRepoToUser

urlpatterns = [
    path('', getTrackedRepos.as_view(), name='user_repos'),
    path("all/", getAllRepos.as_view(), name='all_user_repos'),
    path('add/', AddRepoToUser.as_view(), name='add_repo')
]
