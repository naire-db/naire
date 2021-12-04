from django.urls import path

from . import views


urlpatterns = [
    path('upload_file/', views.upload_file, name='upload_file'),
    path('file/<int:attachment_id>', views.get_file, name='get_file'),
    path('upload_image/', views.upload_image, name='upload_image'),
    path('image/<int:image_id>', views.get_image, name='get_image'),
]
