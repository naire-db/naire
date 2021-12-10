from django.urls import path

from . import views


urlpatterns = [
    path('check_form/', views.check_form, name='check_form'),
    path('create/', views.create, name='create'),
    path('update/', views.update, name='update'),
    path('remove/', views.remove, name='remove'),
    path('get_all/', views.get_all, name='get_all'),
    path('get_detail/', views.get_detail, name='get_detail'),
    path('rename/', views.rename, name='rename'),
]
