from django.urls import path

from . import views


urlpatterns = [
    path('upload_file/', views.upload_file, name='upload_file'),
    path('file/<int:fid>', views.download_file, name='download_file'),
    path('upload_image/', views.upload_image, name='upload_image'),
    path('image/<int:iid>', views.download_image, name='download_image'),
]
