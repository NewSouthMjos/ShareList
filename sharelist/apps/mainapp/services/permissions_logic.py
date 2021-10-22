from accounts.models import CustomUser
from mainapp.models import UserList, UserListCustomUser_ReadOnly, UserListCustomUser_ReadWrite


def add_permission(
    userlist_id: int,
    user_id: int,
    sharelink: str,
    mode: str
    ):

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

    try:
        changing_userlist = UserList.objects.get(id=userlist_id)
    except UserList.DoesNotExist:
        raise LookupError('UserList not found')

    if mode != "readonly" or mode != "readwrite":
        raise ValueError('Wrong mode passed. Use mode = "readonly" or "readwrite"')

    if changing_userlist.author != acting_user_id:
        raise ValueError("Author of this list is another user")
    
    try:
        if mode == "readonly":
            UserListCustomUser_ReadOnly.object.get(customuser=user_id, userlist=userlist_id).delete()
            UserListCustomUser_ReadWrite.object.get(customuser=user_id, userlist=userlist_id).delete()
        elif mode == "readwrite":
            UserListCustomUser_ReadWrite.object.get(customuser=user_id, userlist=userlist_id).delete()
    except UserListCustomUser_ReadOnly.DoesNotExist or UserListCustomUser_ReadOnly.DoesNotExist:
        raise ValueError("Deleting permission does not exist")
        
    