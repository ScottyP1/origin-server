from django.contrib import admin

# Register your models here.
from .models import Repo

admin.site.register(Repo)