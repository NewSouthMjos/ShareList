from accounts.models import CustomUser
from mainapp.models import UserList, UserListCustomUser_ReadOnly, UserListCustomUser_ReadWrite


def add_permission_readonly(userlist_id, user_id, sharelink):
    try:
        changing_userlist = UserList.objects.get(id=userlist_id)
    except UserList.DoesNotExist:
        raise LookupError('UserList not found')
    if not(changing_userlist.sharelink_readonly == sharelink):
        raise ValueError('Wrong sharelink code')
    user=CustomUser.objects.get(id=user_id)
    jointable_records = UserListCustomUser_ReadOnly.objects.filter(customuser=user, userlist=changing_userlist.id)
    if len(jointable_records) >= 1:
        raise ValueError("Permissions already granted")
    UserListCustomUser_ReadOnly.objects.create(
        customuser = user,
        userlist = changing_userlist
    )



def main():
    pass

if __name__ == "__main__":
    main()