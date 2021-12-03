from django import forms
from django.contrib.auth.forms import (
    UserCreationForm, UserChangeForm, AuthenticationForm
)
from django.contrib.auth.forms import UsernameField
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = CustomUser
        fields = UserCreationForm.Meta.fields
        
class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = UserChangeForm.Meta.fields

class CustomUserAuthenticationForm(AuthenticationForm):
    username = UsernameField(widget=forms.TextInput(attrs={
        'autofocus': True,
        'placeholder': 'Имя пользователя'
    }))
    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'current-password',
            'placeholder': 'Пароль',
        }),
    )