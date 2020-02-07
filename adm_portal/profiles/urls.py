from django.urls import path

from .views import profiles_view, upload_file_view

urlpatterns = [path("", profiles_view), path("upload-example", upload_file_view)]
