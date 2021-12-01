from django.urls import path

from . import views

urlpatterns = [
    path('hello/', views.hello, name='hello'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('info/', views.info, name='info'),
    path('register/', views.register, name='register'),
    path('save_profile/', views.save_profile, name='save_profile'),
    path('change_password/', views.change_password, name='change_password'),
    path('create_org/', views.create_org, name='create_org'),
]
