# home/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, ProPlugin, AlternativePlugin


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = [
        "email",
        "username",
        "is_staff",
        "is_active",
    ]


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(ProPlugin)
admin.site.register(AlternativePlugin)