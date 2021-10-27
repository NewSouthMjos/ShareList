from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from mainapp.models import UserList, UserItem, UserListCustomUser_ReadOnly, UserListCustomUser_ReadWrite
from mainapp.services.list_item_logic import get_all_userlists, get_userlist_detail

from django.http import HttpResponse
from django.forms import inlineformset_factory
from mainapp.forms import CustomInlineFormSet


class StartPage(View):
    def get(self, request):
        return render(request, "startpage.html")


class MainPage(LoginRequiredMixin, View):
    login_url = reverse_lazy('login')
    
    def get(self, request):
        userlists = get_all_userlists(request.user.id)
        return render(request, "mainpage.html", userlists)


class DetailList(LoginRequiredMixin, View):
    login_url = reverse_lazy('login')

    def get(self, request, userlist_id):
        try:
            form_userlist = get_userlist_detail(request.user.id, userlist_id)
        except ValueError:
            html = "<html><body>You have no access to list #%s.</body></html>" % userlist_id
            return HttpResponse(html)
        except LookupError:
            html = "<html><body>The list #%s was not found on server.</body></html>" % userlist_id
            return HttpResponse(html)

        ListFormSet = inlineformset_factory(
            UserList, UserItem, fields=('text', 'status', 'last_update_author', 'updated_datetime'), extra=1, formset=CustomInlineFormSet
        ) 
        userlist_obj = UserList.objects.get(id=userlist_id)
        formset = ListFormSet(instance=userlist_obj)
        return render(request, "detailpage.html", {"form": form_userlist, "formset": formset})

    def post(self, request, userlist_id):
        ListFormSet = inlineformset_factory(
            UserList, UserItem, fields=('text', 'status', 'last_update_author', 'updated_datetime'), extra=1, formset=CustomInlineFormSet
        )
        userlist_obj = UserList.objects.get(id=userlist_id)
        formset = ListFormSet(request.POST, instance=userlist_obj)
        
        
        if formset.is_valid():
            formset.save()
            return redirect('/lists/')
        else:
            print('Form not valid')

