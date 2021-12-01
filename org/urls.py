from django.urls import path

from . import views

urlpatterns = [
    path('get_joined/', views.get_joined, name='get_joined'),
    path('create/', views.create, name='create'),

    path('get_members/', views.get_members, name='get_members'),
]
