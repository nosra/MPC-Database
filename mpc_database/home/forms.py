# home/forms.py
from django.contrib.auth.forms import AdminUserCreationForm, UserChangeForm, AuthenticationForm
from django import forms
from .models import CustomUser

class CustomUserCreationForm(AdminUserCreationForm):

    class Meta:
        model = CustomUser
        fields = ("username", "email", "avatar")

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ("username", "email", "avatar")

class StaffLoginForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        if not user.is_staff:
            raise forms.ValidationError("Only staff users can log in here.", code="no_staff")
