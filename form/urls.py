from django.urls import path

from . import views

urlpatterns = [
    path('create/', views.create, name='create'),
    path('get_detail/', views.get_detail, name='get_detail'),
    path('save_resp/', views.save_resp, name='save_resp'),
    path('save_title/', views.save_title, name='save_title'),
    path('change_body/', views.change_body, name='change_body'),
    path('remove/', views.remove, name='remove'),

    path('get_form_resps/', views.get_form_resps, name='get_form_resps'),
    path('get_form_stats/', views.get_form_stats, name='get_form_stats'),
    path('get_resp_detail/', views.get_resp_detail, name='get_resp_detail'),
    path('remove_resp/', views.remove_resp, name='remove_resp'),

    path('get_overview/', views.get_overview, name='get_overview'),
    path('get_folder_all/', views.get_folder_all, name='get_folder_all'),
    path('create_folder/', views.create_folder, name='create_folder'),
    path('rename_folder/', views.rename_folder, name='rename_folder'),
    path('remove_folder/', views.remove_folder, name='remove_folder'),
    path('move_to_folder/', views.move_to_folder, name='move_to_folder'),
    path('copy/', views.copy, name='copy'),
]
