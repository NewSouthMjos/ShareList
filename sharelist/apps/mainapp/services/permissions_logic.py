from django.db import IntegrityError, transaction
from django.forms.formsets import BaseFormSet
from django.forms import formset_factory
from django.core.exceptions import (
    PermissionDenied, ObjectDoesNotExist, ValidationError
)

from accounts.models import CustomUser
from mainapp.models import (
    UserList, UserListCustomUser_ReadOnly, UserListCustomUser_ReadWrite
)
from mainapp.forms import UserPermissionForm


class PermissionAlreadyGranted(Exception):
    """Exception for cauth already existing permissions"""

def userlist_access_check(user_id:int, userlist_id: int) -> int:
    """
    Check that userlist_id is exists.
    Return a int stands for access rights for passed userlist_id for
    passed user (user_id).
    0 is no rights,
    1 is only read,
    2 is readwrite,
    3 - user is author of this list (all rights)
    """
    try:
        userlist_obj = UserList.objects.get(id=userlist_id)
    except UserList.DoesNotExist:
        raise ObjectDoesNotExist("List %s not found" % userlist_id)
    if userlist_obj.author.id == user_id:
        return 3
    if len(list(UserListCustomUser_ReadWrite.objects.filter(customuser=user_id, userlist=userlist_id))) > 0:
        return 2
    if len(list(UserListCustomUser_ReadOnly.objects.filter(customuser=user_id, userlist=userlist_id))) > 0:
        return 1
    return 0

def add_permission(
        userlist_id: int, user_id: int, sharelink: str, mode: str):
    """
    Add permission to readonly or read/write of exacly list and exacly
    user to jointable, if properly sharecode was passed to this func
    """
    try:
        changing_userlist = UserList.objects.get(id=userlist_id)
    except UserList.DoesNotExist:
        raise ObjectDoesNotExist('UserList not found')
    if mode == "readonly":
        JoinTable = UserListCustomUser_ReadOnly
        table_sharelink = changing_userlist.sharelink_readonly
    elif mode == "readwrite":
        JoinTable = UserListCustomUser_ReadWrite
        table_sharelink = changing_userlist.sharelink_readwrite
    else:
        raise ValueError('Wrong mode passed. Use mode = "readonly" or "readwrite"')
    if not(table_sharelink == sharelink):
        raise ValueError('Wrong sharelink code')
    try:
        user=CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        raise ObjectDoesNotExist('User not found')
    jointable_records = JoinTable.objects.filter(customuser=user, userlist=changing_userlist.id)
    if len(jointable_records) >= 1:
        raise PermissionAlreadyGranted("Permission already granted")

    #check the access, to raise error if access level is already higher
    if mode == "readonly":
        if userlist_access_check(user_id, userlist_id) >= 1:
            raise PermissionAlreadyGranted("You already have higher privileges for this list")
    if mode == "readwrite":
        if userlist_access_check(user_id, userlist_id) >= 2:
            raise PermissionAlreadyGranted("You already have higher privileges for this list")


    with transaction.atomic():
        #deleting readonly permisson, if readwrite adding:
        if mode == "readwrite":
            JoinTable_readonly = UserListCustomUser_ReadOnly.objects.filter(customuser=user, userlist=changing_userlist.id)
            if len(JoinTable_readonly) >= 1:
                JoinTable_readonly.delete()
        
        JoinTable.objects.create(
            customuser = user,
            userlist = changing_userlist
        )

def add_permission_checker(userlist_id: int, user_id: int, sharelink: str):
    """
    Check information about adding permissions request, and if all is fine - 
    returns title, description and mode = readonly/readwrite
    """
    try:
        changing_userlist = UserList.objects.get(id=userlist_id)
    except UserList.DoesNotExist:
        raise ObjectDoesNotExist('UserList not found')
    if sharelink == changing_userlist.sharelink_readonly:
        mode = "readonly"
    elif sharelink == changing_userlist.sharelink_readwrite:
        mode = "readwrite"
    else:
        raise ValueError('Wrong sharelink code')
    return {
        'title': changing_userlist.title,
        'description': changing_userlist.description,
        'mode': mode}

def detele_permission(
        userlist_id: int, acting_user_id: int, user_id: int, mode: str):
    """
    Delete permissions of readonly or read/write jointable of exacly user and
    exacly list, if user that trying to delete permissions (acting_user_id)
    if author of this list, or acting_user trying to delete himself's access
    """
    if userlist_access_check(acting_user_id, userlist_id) < 3:
            raise PermissionDenied("You not author so you cant delete others \
                permission for this list"
            )
    if not(mode == "readonly" or mode == "readwrite"):
        raise ValueError('Wrong mode passed. Use mode = "readonly" or "readwrite"')
    try:
        if mode == "readonly":
            UserListCustomUser_ReadOnly.objects.get(customuser=user_id, userlist=userlist_id).delete()
        elif mode == "readwrite":
            UserListCustomUser_ReadWrite.objects.get(customuser=user_id, userlist=userlist_id).delete()
    except (UserListCustomUser_ReadOnly.DoesNotExist, UserListCustomUser_ReadWrite.DoesNotExist) as e:
        raise ObjectDoesNotExist("Deleting permission does not exist")

def set_permission(
        userlist_id: int, acting_user_id: int, user_id: int, mode: str):
    """
    sets the permission of exacly list for exacly user to readonly, if user that
    trying to change permissions (acting_user_id) if author of this list
    """
    if userlist_access_check(acting_user_id, userlist_id) < 3:
            raise PermissionDenied("You not author so you cant sets others \
                permission for this list"
            )
    changing_userlist = UserList.objects.get(id=userlist_id)
    
    if not(mode == "readonly"  or mode == "readwrite" or mode == "none"):
        raise ValueError('Wrong mode passed. Use mode = "readonly" or "readwrite" or "none"')

    if mode == "none":
        try:
            detele_permission(userlist_id, acting_user_id, user_id, "readonly")
        except ObjectDoesNotExist:
            pass
        try:
            detele_permission(userlist_id, acting_user_id, user_id, "readwrite")
        except ObjectDoesNotExist:
            pass
        return True

    if mode == "readonly":
        try:
            detele_permission(userlist_id, acting_user_id, user_id, "readwrite")
        except ObjectDoesNotExist:
            pass
        try:
            table_sharelink = changing_userlist.sharelink_readonly
            add_permission(userlist_id, user_id, table_sharelink, "readonly")
            return True
        except PermissionAlreadyGranted as error:
            return True
        except (LookupError, ValueError, ObjectDoesNotExist) as error:
            raise ValueError("Error while adding permissions: "+ str(error.args))

    if mode == "readwrite":
        try:
            detele_permission(userlist_id, acting_user_id, user_id, "readonly")
        except ObjectDoesNotExist:
            pass
        try:
            table_sharelink = changing_userlist.sharelink_readwrite
            add_permission(userlist_id, user_id, table_sharelink, "readwrite")
            return True
        except PermissionAlreadyGranted as error:
            return True
        except (LookupError, ValueError, ObjectDoesNotExist) as error:
            raise ValueError("Error while adding permissions: " + str(error.args))

    raise ValueError("Something went wronge while changing permissions")

def get_permissions(userlist_id: int, acting_user_id: int):
    """Returns formset of all existing permissions for requested userlist"""
    if userlist_access_check(acting_user_id, userlist_id) < 3:
            raise PermissionDenied("You not author so you cant check others \
                permissions for this list"
            )
    permissions_formset = formset_factory(
        UserPermissionForm, formset=BaseFormSet, extra=0
    )
    userlist_obj = UserList.objects.get(id=userlist_id)
    r_records = UserListCustomUser_ReadOnly.objects.filter(userlist=userlist_obj)
    rw_records = UserListCustomUser_ReadWrite.objects.filter(userlist=userlist_obj)
    permissions_data = []
    for record in rw_records:
        permissions_data.append({'username': record.customuser,
                                 'username_id': record.customuser.id,
                                 'access': 'readwrite'})
    for record in r_records:
        permissions_data.append({'username': record.customuser,
                                 'username_id': record.customuser.id,
                                 'access': 'readonly'})
    return permissions_formset(initial=permissions_data)

def save_permissions(request, userlist_id: int):
    """Saves all access options for userlist"""
    permissions_formset = formset_factory(
        UserPermissionForm, formset=BaseFormSet
    )
    permissions_formset_obj = permissions_formset(request.POST)
    if not(permissions_formset_obj.is_valid()):
        print(permissions_formset_obj)
        raise ValidationError('form is not valid')
        #
    for permissions_form in permissions_formset_obj:
        try:
            username_id = permissions_form.cleaned_data.get('username_id')
            user_obj = CustomUser.objects.get(id=username_id)
        except CustomUser.DoesNotExist:
            raise ObjectDoesNotExist("User with id %s not found to save" % username_id)
        set_permission(
            userlist_id,
            request.user.id,
            user_obj.id,
            permissions_form.cleaned_data.get('access'),
        )