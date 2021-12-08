import logging

from django import forms
from django.contrib.auth.forms import (
    UserCreationForm, UserChangeForm, AuthenticationForm, UsernameField
)
from django.contrib.auth.forms import UsernameField
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import password_validation

from mainapp.services.list_item_logic import make_example_userlist

from .models import CustomUser


logger = logging.getLogger(__name__)


class CustromUsernameField(UsernameField):
    """UsernameField redefine for add placeholder"""
    def widget_attrs(self, widget):
        return {
            **super().widget_attrs(widget),
            'placeholder': 'Имя пользователя'
        }


class CustomUserCreationForm(UserCreationForm):
    """
    UserCreationForm redefine for add placeholers and
    custom operation to add default userlist on users
    saves operation
    """
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'new-password',
            'placeholder': 'Введите пароль'
        }),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'new-password',
            'placeholder': 'Повторите пароль'
        }),
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
    )

    class Meta(UserCreationForm):
        model = CustomUser
        fields = UserCreationForm.Meta.fields
        field_classes = {'username': CustromUsernameField}

    def save(self, *args, **kwargs):
        user = super().save(*args, **kwargs)
        logger.info(f"Adding default list for new user '{user.username}'...")
        make_example_userlist(user)
        logger.info(f"Default list for '{user.username}' added!")
        return user
        
class CustomUserChangeForm(UserChangeForm):
    """Not necessary redefine"""
    class Meta:
        model = CustomUser
        fields = UserChangeForm.Meta.fields

class CustomUserAuthenticationForm(AuthenticationForm):
    """UserAuthenticationForm redefine for add placeholders"""
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