from django.urls import path, reverse_lazy
from . import views
from django.contrib.auth import views as auth_views
from .forms import StaffLoginForm

urlpatterns = [
    path('', views.home, name='home'),
    path('plugins', views.plugins, name='plugins'),
    path('plugins/pro/<int:pk>/', views.plugin_detail, name='plugin_detail'),
    path('plugins/alt/<int:pk>/', views.alt_plugin_detail, name='alt_plugin_detail'),
    path("login/", auth_views.LoginView.as_view(template_name="login.html"),  name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="home"), name="logout"),
    path("staff/dashboard/", views.staff_dashboard, name="staff_dashboard"), 
    path("about/", views.about, name="about"),
    path('ajax/search/', views.search_plugins, name='ajax_search')
    
]

