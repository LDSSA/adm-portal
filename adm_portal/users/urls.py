from django.urls import path

from .views import login_view, logout_view, signup_view

urlpatterns = [path("signup", signup_view), path("login", login_view), path("logout", logout_view)]
