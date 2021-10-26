from django.views import View
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from mainapp.models import UserList, UserListCustomUser_ReadOnly, UserListCustomUser_ReadWrite
from mainapp.services.list_item_logic import get_all_userlists, get_userlist_detail

from django.http import HttpResponse


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
        return render(request, "detailpage.html", {"form": form_userlist})