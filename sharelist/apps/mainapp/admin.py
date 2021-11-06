from django.contrib import admin
from mainapp.models import UserList, UserItem, UserListCustomUser_ReadOnly, UserListCustomUser_ReadWrite


admin.site.register(UserList)
admin.site.register(UserItem)
admin.site.register(UserListCustomUser_ReadOnly)
admin.site.register(UserListCustomUser_ReadWrite)