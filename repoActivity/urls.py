from django.urls import path
from .views import AllRepoActivity

urlpatterns = [
    path('', AllRepoActivity.as_view(), name='user-activity'),
]
