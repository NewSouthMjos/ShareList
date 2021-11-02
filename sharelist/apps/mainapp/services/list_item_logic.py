from mainapp.models import UserList, UserItem, UserListCustomUser_ReadOnly, UserListCustomUser_ReadWrite
from mainapp.forms import UserListForm, UserItemForm

from django.forms.formsets import BaseFormSet
from django.forms import formset_factory
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied


def get_userlist_detail_context(user_id:int, userlist_id: int):
    return {
        'userlist_form': get_userlist_detail_main(user_id, userlist_id),
        'item_formset': get_userlist_detail_items(user_id, userlist_id)
    }

def get_all_userlists(user_id: int):
    """Return all the userlists, that user can see 
    (he is author, he has permissions to read or read/write)"""
    userlists_byauthor = UserList.objects.filter(author=user_id)
    userlists_readonly = UserList.objects.filter(
        userlistcustomuser_readonly__in = UserListCustomUser_ReadOnly.objects.filter(customuser=user_id)
    )
    userlists_readwrite = UserList.objects.filter(
        userlistcustomuser_readwrite__in = UserListCustomUser_ReadWrite.objects.filter(customuser=user_id)
    )
    userlists = {
        "userlists_byauthor": userlists_byauthor,
        "userlists_readwrite": userlists_readwrite,
        "userlists_readonly": userlists_readonly,
    }
    return userlists

def get_userlist_detail_main(user_id: int, userlist_id: int):
    """return the form of UserList to be displayed,
    if there is access to this list"""
    #userlist exist check
    try:
        userlist_obj = UserList.objects.get(id=userlist_id)
    except UserList.DoesNotExist:
        raise ObjectDoesNotExist("The list #%s was not found on server." % userlist_id)
    if userlist_access_check(user_id, userlist_id) < 1:
        raise PermissionDenied("You have no access to list #%s." % userlist_id)
    return UserListForm(initial={'title': userlist_obj.title, 'description': userlist_obj.description})

def get_userlist_detail_items(user_id: int, userlist_id: int):
    ItemFormSet = formset_factory(UserItemForm, formset=BaseFormSet)
    items_in_requested_list = UserItem.objects.filter(related_userlist=userlist_id)
    item_data = [{'text': i.text, 'status': i.status} for i in items_in_requested_list]
    return ItemFormSet(initial=item_data)

def userlist_access_check(user_id:int, userlist_id: int) -> int:
    """
    return a int stands for access rights for passed userlist_id for
    passed user (user_id).
    0 is no rights,
    1 is only read,
    2 is readwrite,
    3 - user is author of this list (all rights)
    """
    userlist_obj = UserList.objects.get(id=userlist_id)
    if userlist_obj.author.id == user_id:
        return 3
    if len(list(UserListCustomUser_ReadWrite.objects.filter(customuser=user_id, userlist=userlist_id))) > 0:
        return 2
    if len(list(UserListCustomUser_ReadOnly.objects.filter(customuser=user_id, userlist=userlist_id))) > 0:
        return 1
    return 0


    
    
    