from django.urls import path

from . import views

app_name = 'form'
urlpatterns = [
    path('get_all/', views.get_all, name='get_all'),
    path('create/', views.create, name='create'),
]
