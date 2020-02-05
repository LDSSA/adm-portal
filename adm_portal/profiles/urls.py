from django.urls import path

from .views import profiles_view

urlpatterns = [path("", profiles_view)]
