from accounts.models import CustomUser
from mainapp.models import UserList, UserListCustomUser_ReadOnly, UserListCustomUser_ReadWrite


def add_permission(
    userlist_id: int,
    user_id: int,
    sharelink: str,
    mode: str
    ):
    """add permission to readonly or read/write of exacly list and exacly
    user to jointable, if properly sharecode was passed to this func"""

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
    user=CustomUser.objects.get(id=user_id)
    jointable_records = JoinTable.objects.filter(customuser=user, userlist=changing_userlist.id)
    if len(jointable_records) >= 1:
        raise ValueError("Permission already granted")
    if mode == "readonly":
        JoinTable_readwrite = UserListCustomUser_ReadWrite.objects.filter(customuser=user, userlist=changing_userlist.id)
        if len(JoinTable_readwrite) >= 1:
            raise ValueError("You already have high privileges for this list")
    
    JoinTable.objects.create(
        customuser = user,
        userlist = changing_userlist
    )

def detele_permission(
    userlist_id: int,
    acting_user_id: int,
    user_id: int,
    mode: str
    ):
    """delete permissions of readonly or read/write jointable of exacly user and
    exacly list, if user that trying to delete permissions (acting_user_id)
    if author of this list"""

    try:
        changing_userlist = UserList.objects.get(id=userlist_id)
    except UserList.DoesNotExist:
        raise LookupError('UserList not found')

    if not(mode == "readonly"  or mode == "readwrite"):
        raise ValueError('Wrong mode passed. Use mode = "readonly" or "readwrite"')

    if changing_userlist.author.id != acting_user_id:
        raise ValueError("Author of this list is another user")
    
    try:
        if mode == "readonly":
            UserListCustomUser_ReadOnly.objects.get(customuser=user_id, userlist=userlist_id).delete()
        elif mode == "readwrite":
            UserListCustomUser_ReadWrite.objects.get(customuser=user_id, userlist=userlist_id).delete()
    except (UserListCustomUser_ReadOnly.DoesNotExist, UserListCustomUser_ReadWrite.DoesNotExist) as e:
        raise LookupError("Deleting permission does not exist")

def set_permissions(
    userlist_id: int,
    acting_user_id: int,
    user_id: int,
    mode: str,
    ):
    """sets the permission of exacly list for exacly user to readonly, if user that
     trying to change permissions (acting_user_id) if author of this list """

    try:
        changing_userlist = UserList.objects.get(id=userlist_id)
    except UserList.DoesNotExist:
        raise LookupError('UserList not found')
    if changing_userlist.author != acting_user_id:
        raise ValueError("Author of this list is another user")
    if not(mode == "readonly"  or mode == "readwrite" or mode == "none"):
        raise ValueError('Wrong mode passed. Use mode = "readonly" or "readwrite" or "none"')

    if mode == "none":
        try:
            detele_permission(userlist_id, acting_user_id, user_id, "readonly")
        finally:
            pass
        try:
            detele_permission(userlist_id, acting_user_id, user_id, "readwrite")
        finally:
            pass
        return True

    if mode == "readonly":
        try:
            detele_permission(userlist_id, acting_user_id, user_id, "readwrite")
        finally:
            pass
        try:
            table_sharelink = changing_userlist.sharelink_readonly
            add_permission(userlist_id, acting_user_id, table_sharelink, "readonly")
            return True
        finally:
            pass

    if mode == "readwrite":
        try:
            detele_permission(userlist_id, acting_user_id, user_id, "readonly")
        finally:
            pass
        try:
            table_sharelink = changing_userlist.sharelink_readwrite
            add_permission(userlist_id, acting_user_id, table_sharelink, "readwrite")
            return True
        finally:
            pass

    raise ValueError("Something went wronge while changing permissions")