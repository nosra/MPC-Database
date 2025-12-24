from django.urls import path, reverse_lazy
from . import views
from django.contrib.auth import views as auth_views
from .forms import StaffLoginForm

urlpatterns = [
    path('', views.home, name='home'),
    path('plugins', views.plugins, name='plugins'),
    path('plugins/pro/<int:pk>/', views.plugin_detail, name='plugin_detail'),
    path('plugins/alt/<int:pk>/', views.alt_plugin_detail, name='alt_plugin_detail'),
    path(
        "staff_login/",
        auth_views.LoginView.as_view(
            template_name="staff_login.html",
            authentication_form=StaffLoginForm,
            next_page=reverse_lazy("staff_dashboard"),
        ),
        name="staff_login",
    ),
    path("staff_logout/", auth_views.LogoutView.as_view(next_page="staff_login"), name="staff_logout"),
    path("staff_dashboard/", views.staff_dashboard, name="staff_dashboard"),
    path("about/", views.about, name="about"),
    path('ajax/search/', views.search_plugins, name='ajax_search')
    
]

