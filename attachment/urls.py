from django.urls import path

from . import views


urlpatterns = [
    path('upload_file/', views.upload_file, name='upload_file'),
    path(r'file/<int:fid>', views.download_file, name='download_file'),
]
