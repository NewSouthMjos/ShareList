from django.forms import ModelForm, fields
from mainapp.models import UserList


class UserListForm(ModelForm):
    class Meta:
        model = UserList
        fields = ['title', 'description']