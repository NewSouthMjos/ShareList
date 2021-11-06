from django import forms
#from django.forms import ModelForm, fields
from mainapp.models import UserList
#from django.forms import BaseInlineFormSet
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