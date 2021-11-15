from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.forms.formsets import BaseFormSet
from django.forms import formset_factory

from mainapp.services.list_item_logic import (
    get_all_userlists, get_userlist_detail_context, 
    get_userlist_detail_maininfo, save_userlist_detail_all,
    delete_userlist, create_userlist,
    get_userlist_detail_sharelinks
)
from mainapp.services.permissions_logic import (
    add_permission_checker, add_permission, detele_permission, get_permissions,
    save_permissions, userlist_access_check
)
from mainapp.forms import UserListForm, UserItemForm



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


class CreateList(LoginRequiredMixin, BaseView):
    """
    View of creating new list with items
    """
    login_url = reverse_lazy('login')

    def get(self, request):
        context = {
            'userlist_form': UserListForm,
            'item_formset': formset_factory(
                UserItemForm, formset=BaseFormSet, extra=1
            )
        }
        return render(request, "detailpage.html", context)

    def post(self, request):
        userlist_id = create_userlist(request)
        return redirect(reverse('detailpage', args=[int(userlist_id)]))


class DeleteList(LoginRequiredMixin, BaseView):
    """
    View of deleting list
    """
    login_url = reverse_lazy('login')

    def get(self, request, userlist_id):
        context = {'userlist_form': get_userlist_detail_maininfo(
            request.user.id,
            userlist_id
        )}
        return render(request, "deletepage.html", context)

    def post(self, request, userlist_id):
        delete_userlist(request.user.id, userlist_id)
        return redirect(reverse('mainpage'))


class RemoveList(LoginRequiredMixin, BaseView):
    """
    View of removing access for user for exacly list.
    List remains untouched.
    """
    login_url = reverse_lazy('login')

    def get(self, request, userlist_id):
        context = {'userlist_form': get_userlist_detail_maininfo(
            request.user.id,
            userlist_id
        )}
        return render(request, "removelist.html", context)

    def post(self, request, userlist_id):
        access_level = userlist_access_check(request.user.id, userlist_id)
        print(access_level)
        if access_level == 2:
            mode = 'readwrite'
        elif access_level == 1:
            mode = 'readonly'
        else:
            raise ValueError('Privilegies error')
        detele_permission(userlist_id, request.user.id, request.user.id, mode)
        return redirect(reverse('mainpage'))


class ShareListConfirm(LoginRequiredMixin, BaseView):
    """Adding users permissions, if sharecode is right"""
    login_url = reverse_lazy('login')

    def get(self, request, userlist_id, sharecode):
        context = add_permission_checker(
            userlist_id, request.user.id, sharecode
        )
        return render(request, "sharepage.html", context)

    def post(self, request, userlist_id, sharecode):
        try:
            mode = request.POST['mode']
        except KeyError:
            raise KeyError('Mode = read or readwrite not found')
        add_permission(userlist_id, request.user.id, sharecode, mode)
        return redirect(reverse('mainpage'))


class UserListControl(LoginRequiredMixin, BaseView):
    """
    Control page for author of UserList, where he can change permissions for
    users and check the sharecode for list
    """
    login_url = reverse_lazy('login')

    def get(self, request, userlist_id):
        context = {'userlist_form': get_userlist_detail_maininfo(
                        request.user.id,
                        userlist_id),
                   'userlistshareform': get_userlist_detail_sharelinks(
                        request,
                        userlist_id),
                    'permissions_formset': get_permissions(
                        userlist_id,
                        request.user.id)
                   }
        return render(request, "controllist.html", context)

    def post(self, request, userlist_id):
        save_permissions(request, userlist_id)
        return redirect(reverse('controllist', args=[userlist_id]))


