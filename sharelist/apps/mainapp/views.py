from django.views import View
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied

from mainapp.services.list_item_logic import (
    get_all_userlists, get_userlist_detail_context,
    save_userlist_detail_all
)


class BaseView(View):
    """
    Base view for handle exceptions.
    All other views should be child of this view
    """
    def dispatch(self, request, *args, **kwargs):
        try:
            response = super().dispatch(request, *args, **kwargs)
        except Exception as e:
            html = "<html><body>%s</body></html>" % e
            if type(e) == PermissionDenied:
                status_code = 403
            elif type(e) == ObjectDoesNotExist:
                status_code = 404
            else:
                status_code = 500
            return HttpResponse(html, status=status_code)
        return response


class StartPage(BaseView):
    """Start page, that displays to all unauthentication users"""
    def get(self, request):
        return render(request, "startpage.html")


class MainPage(LoginRequiredMixin, BaseView):
    """Page that contains all the userlist, avalible to user"""
    login_url = reverse_lazy('login')
    
    def get(self, request):
        userlists = get_all_userlists(request.user.id)
        return render(request, "mainpage.html", userlists)


class DetailList(LoginRequiredMixin, BaseView):
    """
    Detail view that contains all the items for userlist.
    User can save changes by POST request
    """
    login_url = reverse_lazy('login')
    def get(self, request, userlist_id):
        context = get_userlist_detail_context(request.user.id, userlist_id)
        return render(request, "detailpage.html", context)

    def post(self, request, userlist_id):
        userlist_form, item_formset = save_userlist_detail_all(request, userlist_id)
        context = {
            'userlist_form': userlist_form,
            'item_formset': item_formset,
        }
        return render(request, "detailpage.html", context)


