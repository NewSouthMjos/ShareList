from mainapp.models import UserList, UserItem, UserListCustomUser_ReadOnly, UserListCustomUser_ReadWrite
from mainapp.forms import UserListForm


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
        "userlists_readonly": userlists_readonly,
        "userlists_readwrite": userlists_readwrite,
    }
    return userlists

def get_userlist_detail(user_id:int, userlist_id: int):
    
    #userlist exist check
    try:
        userlist_obj = UserList.objects.get(id=userlist_id)
    except UserList.DoesNotExist:
        raise LookupError("Userlist doesnt exist")
    
    #access check
    if userlist_obj.author.id == user_id:
        is_author = True
    else:
        is_author = False

    if len(list(UserListCustomUser_ReadOnly.objects.filter(customuser=user_id, userlist=userlist_id))) > 0:
        is_readonly_access = True
    else:
        is_readonly_access = False

    if len(list(UserListCustomUser_ReadWrite.objects.filter(customuser=user_id, userlist=userlist_id))) > 0:
        is_readwrite_access = True
    else:
        is_readwrite_access = False

    if not(is_author or is_readonly_access or is_readwrite_access):
        raise ValueError("No access")

    return UserListForm(instance=userlist_obj)

    
    
    