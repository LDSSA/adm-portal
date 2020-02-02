from django.contrib import admin
from django.urls import path

from profiles.views import profiles_view

from .views import hello_view, ping_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("profiles/", profiles_view),
    path("ping", ping_view),
    path("", hello_view),
]
