# home/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, ProPlugin, AlternativePlugin, AudioDemo


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
     # show avatar on the change form
    fieldsets = UserAdmin.fieldsets + (
        ("Profile", {"fields": ("avatar",)}),
    )

    # show avatar on the add form
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {"fields": ("avatar",)}),
    )


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(ProPlugin)
admin.site.register(AlternativePlugin)
admin.site.register(AudioDemo)