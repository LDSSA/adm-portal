from django.contrib import admin
from django.urls import include, path

from .views import hello_view, ping_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("users/", include("users.urls")),
    path("profiles/", include("profiles.urls")),
    path("ping", ping_view),
    path("", hello_view),
]
