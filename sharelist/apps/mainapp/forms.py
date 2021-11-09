from django import forms
from mainapp.models import UserList
from django.utils import timezone
from accounts.models import CustomUser


class UserItemForm(forms.Form):
    """
    Form for representing user items in view, that user
    can change by himself
    """
    text = forms.CharField(
        max_length=1000,
        widget=forms.TextInput(attrs={
            'placeholder': 'Добавьте новый пункт...',
            }),
        required=False
    )
    status = forms.ChoiceField(
        choices=[
            ('done', 'Готово'),
            ('in_progress', 'В процессе'),
            ('planned', 'Запланировано'),
        ],
        required=False
    )


class UserListForm(forms.Form):
    """
    Form for representing main information about userlist,
    that user can change by himself
    """
    title = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'Название списка',
            }),
        required=True
    )
    description = forms.CharField(
        max_length=1000,
        widget=forms.TextInput(attrs={
            'placeholder': 'Описание списка',
            }),
        required=False
    )


class UserListShareForm(forms.Form):
    """
    Form for representing sharelinks information of list
    """
    sharelink_readonly = forms.CharField(
        max_length=32,
        widget=forms.TextInput(attrs={
            'readonly': True,
            'size': 40,
            }),
        required=False
    )
    sharelink_readwrite = forms.CharField(
        max_length=32,
        widget=forms.TextInput(attrs={
            'readonly': True,
            'size': 40,
            }),
        required=False
    )