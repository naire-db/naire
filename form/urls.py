from django.urls import path

from . import views

urlpatterns = [
    path('get_all/', views.get_all, name='get_all'),
    path('create/', views.create, name='create'),
    path('get_detail/', views.get_detail, name='get_detail'),
    path('save_resp/', views.save_resp, name='save_resp'),
    path('save_title/', views.save_title, name='save_title'),
    path('change_body/', views.change_body, name='change_body'),
    path('remove/', views.remove, name='remove'),
    path('get_form_resps/', views.get_form_resps, name='get_form_resps'),
    path('get_form_stats/', views.get_form_stats, name='get_form_stats'),
    path('get_resp_detail/', views.get_resp_detail, name='get_resp_detail'),
    path('remove_resp/', views.remove_resp, name='remove_resp')
]
