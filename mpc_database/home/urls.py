from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('plugins', views.plugins, name='plugins'),
    path('plugins/pro/<int:pk>/', views.plugin_detail, name='plugin_detail'),
    path('plugins/alt/<int:pk>/', views.alt_plugin_detail, name='alt_plugin_detail'),
]

