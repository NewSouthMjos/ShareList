from django import forms
#from django.forms import ModelForm, fields
from mainapp.models import UserList
#from django.forms import BaseInlineFormSet
from django.utils import timezone
from accounts.models import CustomUser

class CustomInlineFormSet(forms.BaseInlineFormSet):
    pass
    # def clean(self):
    #     super().clean()
    #     # example custom validation across forms in the formset
    #     for form in self.forms:
    #         # your custom formset validation
    #         now = timezone.now() 
    #         form.cleaned_data['updated_datetime'] = now
    #         form.instance.updated_datetime = now

    #         customuser = CustomUser.objects.get(id=1)
    #         form.cleaned_data['last_update_author'] = customuser
    #         form.instance.last_update_author = customuser
    #         print('Done cleaning data and changind datetime/author!')
    #         print(form.cleaned_data)
        

class UserListForm_old(forms.ModelForm):
    class Meta:
        model = UserList
        fields = ['title', 'description']

    # def clean_title(self):
    #     title = self.cleaned_data['title']
    #     return title

#МЕНЯЕМ СТРУКТУРУ ФОРМ, НИЖЕ - НОВЫЕ


class UserItemForm(forms.Form):
    """
    Form for representing user items in view, that user
    can change by himself
    """
    text = forms.CharField(
        max_length=1000,
        widget=forms.TextInput(attrs={
            'placeholder': 'Заполните пункт...',
            }),
            required=False
    )
    status = forms.ChoiceField(
        choices=[
            ('done', 'Готово'),
            ('in_progress', 'В процессе'),
            ('default', 'Запланировано'),
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