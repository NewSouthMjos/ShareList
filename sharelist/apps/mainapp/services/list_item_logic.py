from django.forms.formsets import BaseFormSet
from django.forms import formset_factory
from django.core.exceptions import (
    ObjectDoesNotExist,
    PermissionDenied,
    ValidationError,
)
from django.utils import timezone
from django.db import IntegrityError, transaction

from mainapp.models import (
    UserList,
    UserItem,
    UserListCustomUser_ReadOnly,
    UserListCustomUser_ReadWrite,
)
from mainapp.forms import UserListForm, UserItemForm, UserListShareForm
from mainapp.services.permissions_logic import userlist_access_check
from accounts.models import CustomUser


def get_userlist_detail_context(user_id: int, userlist_id: int):
    """Return all fields of passed userlist_id"""
    return {
        "userlist_form": get_userlist_detail_maininfo(user_id, userlist_id),
        "item_formset": get_userlist_detail_items(user_id, userlist_id),
    }


def get_all_userlists(user_id: int):
    """
    Return all the userlists, that user can see
    (he is author, he has permissions to read or read/write)
    """
    userlists_byauthor = UserList.objects.filter(author=user_id)
    userlists_readonly = UserList.objects.filter(
        userlistcustomuser_readonly__in=UserListCustomUser_ReadOnly.objects.filter(
            customuser=user_id
        )
    )
    userlists_readwrite = UserList.objects.filter(
        userlistcustomuser_readwrite__in=UserListCustomUser_ReadWrite.objects.filter(
            customuser=user_id
        )
    )
    userlists = {
        "userlists_byauthor": userlists_byauthor,
        "userlists_readwrite": userlists_readwrite,
        "userlists_readonly": userlists_readonly,
    }
    return userlists


def get_userlist_detail_maininfo(user_id: int, userlist_id: int):
    """
    Return the form of UserList to be displayed,
    if there is access to this list
    """
    # userlist exist check
    try:
        userlist_obj = UserList.objects.get(id=userlist_id)
    except UserList.DoesNotExist:
        raise ObjectDoesNotExist(
            "The list #%s was not found on server." % userlist_id
        )
    if userlist_access_check(user_id, userlist_id) < 1:
        raise PermissionDenied("You have no access to list #%s." % userlist_id)
    return UserListForm(
        initial={
            "title": userlist_obj.title,
            "description": userlist_obj.description,
            "last_update_author":userlist_obj.last_update_author,
            "updated_datetime":userlist_obj.updated_datetime,
        }
    )


def get_userlist_detail_items(user_id: int, userlist_id: int, extra=1):
    """
    Return item formset, that contains data from
    passed userlist_id
    """
    item_formset = formset_factory(UserItemForm, formset=BaseFormSet, extra=extra)
    items_in_requested_list = UserItem.objects.filter(
        related_userlist=userlist_id
    )
    item_data = [
        {"text": i.text, "status": i.status, 'useritem_id': i.id, 'updated_datetime': i.updated_datetime, 'last_update_author': i.last_update_author} for i in items_in_requested_list
    ]
    return item_formset(initial=item_data)


def save_userlist_detail_all(request, userlist_id):
    """
    Saves all information in userlist, include items
    """

    if userlist_access_check(request.user.id, userlist_id) < 2:
        raise PermissionDenied(
            "You have no access to write list #%s." % userlist_id
        )
    userlist_form = save_userlist_detail_maininfo(request, userlist_id)
    item_formset = save_userlist_detail_items(request, userlist_id)
    return (userlist_form, item_formset)


def create_userlist(request):
    """Creates new list and saves it"""
    userlist_obj = UserList.objects.create_userlist(
        author=request.user,
        created_datetime=timezone.now(),
        updated_datetime=timezone.now(),
        last_update_author=request.user,
        is_public=False,
    )
    userlist_obj.save()
    save_userlist_detail_all(request, userlist_obj.id)
    return userlist_obj.id


def save_userlist_detail_maininfo(request, userlist_id: int):
    """Updates list info from POST request"""
    userlist_form = UserListForm(request.POST)
    if not (userlist_form.is_valid()):
        raise ValidationError("form is not valid")
    userlist_obj = UserList.objects.get(id=userlist_id)
    userlist_obj.title = userlist_form.cleaned_data.get("title")
    userlist_obj.description = userlist_form.cleaned_data.get("description")
    userlist_obj.updated_datetime = timezone.now()
    userlist_obj.last_update_author = request.user
    userlist_obj.save()


def save_userlist_detail_items(request, userlist_id: int):
    """Saves all items from request to userlist"""
    ItemFormSet = formset_factory(UserItemForm, formset=BaseFormSet)
    #print(ItemFormSet)
    #item_formset_f = get_userlist_detail_items(request.user.id, userlist_id, 1)
    #print(item_formset_f)
    item_formset = ItemFormSet(request.POST)
    if not (item_formset.is_valid()):
        #print(item_formset.total_error_count())
        #print(item_formset.errors)
        #print(item_formset.non_form_errors())
        
        raise ValidationError("form is not valid")
    new_items = []
    user_items_old_objects = UserItem.objects.filter(related_userlist=userlist_id)
    for item_form in item_formset:
        if item_form.cleaned_data.get("text"):

            # Check if useritem has changed and exclude it, if it doenst:
            useritem_id = item_form.cleaned_data.get("useritem_id")
            try:
                item_obj = user_items_old_objects.get(id=useritem_id)
                if item_obj.text == item_form.cleaned_data.get("text")\
                    and item_obj.status == item_form.cleaned_data.get("status"):
                    user_items_old_objects = user_items_old_objects.exclude(id=useritem_id)
                    continue
            except UserItem.DoesNotExist:
                pass
            
            # If something changed, add new item:
            new_items.append(
                UserItem(
                    related_userlist=UserList.objects.get(id=userlist_id),
                    text=item_form.cleaned_data.get("text"),
                    status=item_form.cleaned_data.get("status"),
                    last_update_author=request.user,
                    updated_datetime=timezone.now(),
                )
            )
    # Update items in transaction
    try:
        with transaction.atomic():
            user_items_old_objects.delete()
            UserItem.objects.bulk_create(new_items)
            # LOG MESSAGE ABOUT UPDATE HERE <---

    except IntegrityError:  # If the transaction failed
        # messages.error(request, '')
        item_formset.add_error(None, "Ошибка сохранения данных на сервере")


def delete_userlist(user_id: int, userlist_id: int):
    """delete userlist, if there is access for user"""
    if userlist_access_check(user_id, userlist_id) < 3:
        raise PermissionDenied(
            "You have no access to delete list #%s." % userlist_id
        )
    try:
        userlist = UserList.objects.get(id=userlist_id)
    except UserList.DoesNotExist:
        raise ObjectDoesNotExist("List %s not found" % userlist_id)
    userlist.delete()


def get_userlist_detail_sharelinks(request, userlist_id: int):
    """
    Returns a form of UserListShareForm with info about sharelinks
    """
    try:
        userlist = UserList.objects.get(id=userlist_id)
    except UserList.DoesNotExist:
        raise ObjectDoesNotExist("List %s not found" % userlist_id)
    if userlist_access_check(request.user.id, userlist_id) < 3:
        raise PermissionDenied("You have no access to view sharelinks")

    link_readonly = (
        str(request.get_host())
        + "/lists/"
        + str(userlist_id)
        + "/"
        + str(userlist.sharelink_readonly)
    )
    link_readwrite = (
        str(request.get_host())
        + "/lists/"
        + str(userlist_id)
        + "/"
        + str(userlist.sharelink_readwrite)
    )
    return UserListShareForm(
        initial={
            "sharelink_readonly": link_readonly,
            "sharelink_readwrite": link_readwrite,
        }
    )
