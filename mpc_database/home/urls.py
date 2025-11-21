from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('plugins', views.plugins, name='plugins'),
    path('plugins/pro/<int:pk>/', views.plugin_detail, name='plugin_detail'),
]
