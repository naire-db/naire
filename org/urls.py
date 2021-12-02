from django.urls import path

from . import views

urlpatterns = [
    path('get_joined/', views.get_joined, name='get_joined'),
    path('create/', views.create, name='create'),
    path('get_members/', views.get_members, name='get_members'),
    path('leave/', views.leave, name='leave'),

    path('check_invite_token/', views.check_invite_token, name='check_invite_token'),
    path('accept_invite/', views.accept_invite, name='accept_invite'),

    path('get_profile/', views.get_profile, name='get_profile'),
    path('rename/', views.rename, name='rename'),
    path('refresh_invite_token/', views.refresh_invite_token, name='refresh_invite_token'),
    path('remove_member/', views.remove_member, name='remove_member'),
    path('change_role/', views.change_role, name='change_role'),
    path('dissolve/', views.dissolve, name='dissolve'),
]
