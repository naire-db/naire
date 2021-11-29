from django.urls import path

from . import views


urlpatterns = [
    path('upload_file/', views.upload_file, name='upload_file'),
    path('download_file/', views.download_file, name='download_file'),
]
