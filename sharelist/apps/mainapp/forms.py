from django import forms
from django.forms.widgets import HiddenInput
from mainapp.models import UserList
from django.utils import timezone
from accounts.models import CustomUser


class UserItemForm(forms.Form):
    """
    Form for representing user items in view, that user
    can change by himself
    """
    def __init__(self, *args, readonly_flag=False, **kwargs):
        super(UserItemForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if readonly_flag is True:
                field.widget.attrs.update({'readonly':True})

    text = forms.CharField(
        max_length=1000,
        widget=forms.Textarea(
            attrs={
                "placeholder": "Добавьте новый пункт...",
            }
        ),
        required=False,
    )
    status = forms.CharField(
        max_length=30,
        # choices=[
        #     ("done", "Готово"),
        #     ("in_progress", "В процессе"),
        #     ("planned", "Запланировано"),
        # ],
        widget=forms.TextInput(
            attrs={
                "hidden": True,
            }
        ),
        required=False,
    )
    useritem_id = forms.IntegerField(required=False, widget=forms.HiddenInput())
    updated_datetime = forms.DateTimeField(required=False)
    last_update_author = forms.CharField(required=False)
    inner_order = forms.IntegerField(required=False, widget=forms.TextInput(
        attrs={
            "readonly": True,
            "tabindex": "-1",
        })
    )
        


class UserListForm(forms.Form):
    """
    Form for representing main information about userlist,
    that user can change by himself
    """

    def __init__(self, *args, readonly_flag=False, **kwargs):
        super(UserListForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if readonly_flag is True:
                field.widget.attrs.update({'readonly':True})
    
    title = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Название списка",
                "onkeydown": "return event.key != 'Enter';",
            }
        ),
        required=True,
    )
    description = forms.CharField(
        max_length=1000,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Описание списка",
            }
        ),
        required=False,
    )
    updated_datetime = forms.DateTimeField(required=False)
    last_update_author = forms.CharField(required=False)


class UserListShareForm(forms.Form):
    """
    Form for representing sharelinks information of list
    """

    sharelink_readonly = forms.CharField(
        max_length=32,
        widget=forms.TextInput(
            attrs={
                "readonly": True,
                "size": 40,
            }
        ),
        required=False,
    )
    sharelink_readwrite = forms.CharField(
        max_length=32,
        widget=forms.TextInput(
            attrs={
                "readonly": True,
                "size": 40,
            }
        ),
        required=False,
    )


class UserPermissionForm(forms.Form):
    """Form for representing signgle row - user access in list options"""

    username = forms.CharField(max_length=50, required=False)
    username_id = forms.IntegerField(required=True, widget=forms.HiddenInput())
    access = forms.ChoiceField(
        choices=[
            ("readwrite", "Чтение/запись"),
            ("readonly", "Только чтение"),
            ("none", "Удалить доступ"),
        ],
        required=True,
    )
