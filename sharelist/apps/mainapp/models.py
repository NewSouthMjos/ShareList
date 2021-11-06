from django.db import models
import secrets


class UserListManager(models.Manager):
    """Dedicated manager for auto generate sharelink codes"""
    def create_userlist(self, *args, **kwargs):
        userlist = self.create(*args, **kwargs)
        userlist.new_sharelink_readonly()
        userlist.new_sharelink_readwrite()
        return userlist


class UserList(models.Model):
    """
    Main model - list of items, that user will operate.
    Each list has to link with items with one-to-many relation
    """
    title = models.CharField(max_length=300, blank=True)
    author = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.CASCADE,
        related_name='userlist_author'
    )
    description = models.TextField(blank=True)
    created_datetime = models.DateTimeField()
    updated_datetime = models.DateTimeField()
    last_update_author = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.CASCADE,
        related_name='userlist_last_update_author'
    )
    is_public = models.BooleanField(default=False)
    sharelink_readwrite = models.CharField(max_length=16)
    sharelink_readonly = models.CharField(max_length=16)

    objects = UserListManager()

    def new_sharelink_readonly(self):
        self.sharelink_readonly = secrets.token_urlsafe(12)

    def new_sharelink_readwrite(self):
        self.sharelink_readwrite = secrets.token_urlsafe(12)
  

class UserItem(models.Model):
    """Sub main model - item is on thing of the list"""
    related_userlist = models.ForeignKey(
        'UserList',
        on_delete=models.CASCADE,
    )
    text = models.TextField()
    status = models.CharField(max_length=20)
    last_update_author = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.CASCADE,
    )
    updated_datetime = models.DateTimeField()


class UserListCustomUser_ReadOnly(models.Model):
    """Join-table for permissions - readonly"""
    customuser = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.CASCADE
    )
    userlist = models.ForeignKey(
        'UserList',
        on_delete=models.CASCADE
    )


class UserListCustomUser_ReadWrite(models.Model):
    """Join-table for permissions - readwrite"""
    customuser = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.CASCADE
    )
    userlist = models.ForeignKey(
        'UserList',
        on_delete=models.CASCADE
    )