from django.urls import path

from . import views


urlpatterns = [
    path('get_logs/', views.get_logs, name='get_logs'),
]
