from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('client.urls')),
    path('api/repos/', include('repo.urls')),
    path('api/activity/', include('repoActivity.urls')),
    path('api/social/', include('socialAccounts.urls'))
]
