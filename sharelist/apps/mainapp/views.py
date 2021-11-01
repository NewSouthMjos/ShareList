from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db import IntegrityError, transaction
from mainapp.models import UserList, UserItem, UserListCustomUser_ReadOnly, UserListCustomUser_ReadWrite
from mainapp.services.list_item_logic import get_all_userlists, get_userlist_detail

from django.http import HttpResponse
from django.forms import inlineformset_factory, formset_factory
from mainapp.forms import CustomInlineFormSet, UserListForm, UserItemForm
from django.forms.formsets import BaseFormSet

from django.utils import timezone



class StartPage(View):
    def get(self, request):
        return render(request, "startpage.html")


class MainPage(LoginRequiredMixin, View):
    login_url = reverse_lazy('login')
    
    def get(self, request):
        userlists = get_all_userlists(request.user.id)
        return render(request, "mainpage.html", userlists)


#Новая классная функция отображения.
#Вся логика пока внутри, перенести ей в бизнес-логику
class DetailList(LoginRequiredMixin, View):
    login_url = reverse_lazy('login')
    def get(self, request, userlist_id):

        #NOT WORKING ACCESS CHECKOUT:
        # try:
        #     form_userlist = get_userlist_detail(request.user.id, userlist_id)
        # except ValueError:
        #     html = "<html><body>You have no access to list #%s.</body></html>" % userlist_id
        #     return HttpResponse(html)
        # except LookupError:
        #     html = "<html><body>The list #%s was not found on server.</body></html>" % userlist_id
        #     return HttpResponse(html)
        user = request.user
        ItemFormSet = formset_factory(UserItemForm, formset=BaseFormSet)
        items_in_requested_list = UserItem.objects.filter(related_userlist=userlist_id)
        item_data = [{'text': i.text, 'status': i.status} for i in items_in_requested_list]
        item_formset = ItemFormSet(initial=item_data)
        userlist_obj = UserList.objects.get(id=userlist_id)
        userlist_form = UserListForm(initial={'title': userlist_obj.title, 'description': userlist_obj.description})
        context = {
            'userlist_form': userlist_form,
            'item_formset': item_formset,
        }
        return render(request, "detailpage.html", context)

    def post(self, request, userlist_id):
        userlist_form = UserListForm(request.POST)
        ItemFormSet = formset_factory(UserItemForm, formset=BaseFormSet)
        item_formset = ItemFormSet(request.POST)

        new_items = []
        if userlist_form.is_valid() and item_formset.is_valid():
            for item_form in item_formset:
                if item_form.cleaned_data.get('text'):
                    new_items.append(UserItem(
                        related_userlist=UserList.objects.get(id=userlist_id),
                        text=item_form.cleaned_data.get('text'),
                        status=item_form.cleaned_data.get('status'),
                        last_update_author=request.user,
                        updated_datetime=timezone.now(),
                    ))

            #Update list info  
            userlist_obj = UserList.objects.get(id=userlist_id)
            userlist_obj.title = userlist_form.cleaned_data.get('title')
            userlist_obj.description = userlist_form.cleaned_data.get('description')
            userlist_obj.updated_datetime = timezone.now()
            userlist_obj.last_update_author = request.user
            userlist_obj.save()

            #Update items in transaction
            try:
                with transaction.atomic():
                    UserItem.objects.filter(related_userlist=userlist_id).delete()
                    UserItem.objects.bulk_create(new_items)
                    # And notify our users that it worked
                    print('SUCCESS! we have UPDATE YOUR DATA!')

            except IntegrityError: #If the transaction failed
                messages.error(request, 'There was an error saving your profile.')
                return redirect(reverse('profile-settings'))
        
        context = {
            'userlist_form': userlist_form,
            'item_formset': item_formset,
        }
        return render(request, "detailpage.html", context)


