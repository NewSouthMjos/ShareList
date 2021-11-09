from accounts.models import CustomUser
from mainapp.models import (
    UserList, UserListCustomUser_ReadOnly, UserListCustomUser_ReadWrite
)
from django.db import IntegrityError, transaction
from mainapp.services.list_item_logic import userlist_access_check

def add_permission(
        userlist_id: int, user_id: int, sharelink: str, mode: str):
    """
    Add permission to readonly or read/write of exacly list and exacly
    user to jointable, if properly sharecode was passed to this func
    """
    try:
        changing_userlist = UserList.objects.get(id=userlist_id)
    except UserList.DoesNotExist:
        raise LookupError('UserList not found')
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
        raise LookupError('User not found')
    jointable_records = JoinTable.objects.filter(customuser=user, userlist=changing_userlist.id)
    if len(jointable_records) >= 1:
        raise ValueError("Permission already granted")

    #check the access, to raise error if access level is already higher
    if mode == "readonly":
        if userlist_access_check(user_id, userlist_id) >= 1:
            raise ValueError("You already have higher privileges for this list")
    if mode == "readwrite":
        if userlist_access_check(user_id, userlist_id) >= 2:
            raise ValueError("You already have higher privileges for this list")


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
        raise LookupError('UserList not found')
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
    try:
        changing_userlist = UserList.objects.get(id=userlist_id)
    except UserList.DoesNotExist:
        raise LookupError('UserList not found')
    if not(mode == "readonly" or mode == "readwrite"):
        raise ValueError('Wrong mode passed. Use mode = "readonly" or "readwrite"')
    if not(changing_userlist.author.id == acting_user_id 
           or acting_user_id == user_id):
        raise ValueError("You have no access to change this permission")
    try:
        if mode == "readonly":
            UserListCustomUser_ReadOnly.objects.get(customuser=user_id, userlist=userlist_id).delete()
        elif mode == "readwrite":
            UserListCustomUser_ReadWrite.objects.get(customuser=user_id, userlist=userlist_id).delete()
    except (UserListCustomUser_ReadOnly.DoesNotExist, UserListCustomUser_ReadWrite.DoesNotExist) as e:
        raise LookupError("Deleting permission does not exist")

def set_permissions(
        userlist_id: int, acting_user_id: int, user_id: int, mode: str):
    """
    sets the permission of exacly list for exacly user to readonly, if user that
    trying to change permissions (acting_user_id) if author of this list
    """

    try:
        changing_userlist = UserList.objects.get(id=userlist_id)
    except UserList.DoesNotExist:
        raise LookupError('UserList not found')
    if changing_userlist.author.id != acting_user_id:
        raise ValueError("Author of this list is another user")
    if not(mode == "readonly"  or mode == "readwrite" or mode == "none"):
        raise ValueError('Wrong mode passed. Use mode = "readonly" or "readwrite" or "none"')

    if mode == "none":
        try:
            detele_permission(userlist_id, acting_user_id, user_id, "readonly")
        except LookupError:
            pass
        try:
            detele_permission(userlist_id, acting_user_id, user_id, "readwrite")
        except LookupError:
            pass
        return True

    if mode == "readonly":
        try:
            detele_permission(userlist_id, acting_user_id, user_id, "readwrite")
        except LookupError:
            pass
        try:
            table_sharelink = changing_userlist.sharelink_readonly
            add_permission(userlist_id, user_id, table_sharelink, "readonly")
            return True
        except (LookupError, ValueError) as error:
            raise ValueError("Error while adding permissions: "+ str(error.args))

    if mode == "readwrite":
        try:
            detele_permission(userlist_id, acting_user_id, user_id, "readonly")
        except LookupError:
            pass
        try:
            table_sharelink = changing_userlist.sharelink_readwrite
            add_permission(userlist_id, user_id, table_sharelink, "readwrite")
            return True
        except (LookupError, ValueError) as error:
            raise ValueError("Error while adding permissions: " + str(error.args))

    raise ValueError("Something went wronge while changing permissions")