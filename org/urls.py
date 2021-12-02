from django.urls import path

from . import views

urlpatterns = [
    path('get_joined/', views.get_joined, name='get_joined'),
    path('get_members/', views.get_members, name='get_members'),
    path('create/', views.create, name='create'),

    path('check_invite_token/', views.check_invite_token, name='check_invite_token'),
    path('accept_invite/', views.accept_invite, name='accept_invite'),

    path('get_profile/', views.get_profile, name='get_profile'),
    path('rename/', views.rename, name='rename'),
    path('refresh_invite_token/', views.refresh_invite_token, name='refresh_invite_token')
]
