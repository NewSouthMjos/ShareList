from django.forms import ModelForm, fields
from mainapp.models import UserList
from django.forms import BaseInlineFormSet
from django.utils import timezone
from accounts.models import CustomUser

class CustomInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        # example custom validation across forms in the formset
        for form in self.forms:
            # your custom formset validation
            now = timezone.now() 
            form.cleaned_data['updated_datetime'] = now
            form.instance.updated_datetime = now

            customuser = CustomUser.objects.get(id=1)
            form.cleaned_data['last_update_author'] = customuser
            form.instance.last_update_author = customuser
            print('Done cleaning data and changind datetime/author!')
            print(form.cleaned_data)
        

class UserListForm(ModelForm):
    class Meta:
        model = UserList
        fields = ['title', 'description']