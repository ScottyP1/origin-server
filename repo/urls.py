from django.urls import path
from .views import getUserRepo, AddRepoToUser

urlpatterns = [
    path('', getUserRepo.as_view(), name='user-repos'),
    path('add/', AddRepoToUser.as_view(), name='add-repo')
]
