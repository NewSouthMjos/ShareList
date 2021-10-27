from django.test import TestCase
from accounts.models import CustomUser
from mainapp.models import (
    UserList,
    UserItem,
    UserListCustomUser_ReadOnly,
    UserListCustomUser_ReadWrite
)
from mainapp.services.list_item_logic import get_all_userlists, get_userlist_detail
from django.utils import timezone


class TestListItemLogicCase(TestCase):

    def setUp(self):
        testuser1 = CustomUser.objects.create_user(
            username='testuser1',
            password='secret1',
        )
        testuser1.save()
        testuser2 = CustomUser.objects.create_user(
            username='testuser2',
            password='secret2',
        )
        testuser2.save()

        testuser3 = CustomUser.objects.create_user(
            username='testuser3',
            password='secret3',
        )
        testuser3.save()

        listtitles = ['First', 'Second', 'Third', 'MyJobs', 'ToDoThings']
        for cur_list_numb in range(len(listtitles)):
            userlist_obj = UserList.objects.create_userlist(
                title = str(listtitles[cur_list_numb]),
                author = CustomUser.objects.get(username='testuser1'),
                description = f'This is {cur_list_numb} testlist, using for test the lists',
                created_datetime = timezone.now(),
                updated_datetime = timezone.now(),
                last_update_author = CustomUser.objects.get(username='testuser1'),
                is_public = False,
            )
            userlist_obj.save()

        userlist1 = UserList.objects.get(title='First')

        userlist2 = UserList.objects.get(title='Second')
        text_list = ['123', '456', '789']
        for cur_text_numb in range(3):
            useritem_obj = UserItem.objects.create(
                related_userlist = userlist2,
                text = text_list[cur_text_numb],
                status = 'done',
                last_update_author = CustomUser.objects.get(username='testuser2'),
                updated_datetime = timezone.now(),
            )
            useritem_obj.save()

        userlist3 = UserList.objects.get(title='Third')
        text_list = ['foo_1', 'foo_2', 'foo_3']
        for cur_text_numb in range(3):
            useritem_obj = UserItem.objects.create(
                related_userlist = userlist3,
                text = text_list[cur_text_numb],
                status = 'in_progess',
                last_update_author = CustomUser.objects.get(username='testuser1'),
                updated_datetime = timezone.now(),
            )
            useritem_obj.save()

        userlist4 = UserList.objects.get(title='MyJobs')
        text_list = ['translator', 'doctor', 'driver']
        for cur_text_numb in range(3):
            useritem_obj = UserItem.objects.create(
                related_userlist = userlist4,
                text = text_list[cur_text_numb],
                status = 'not_done',
                last_update_author = CustomUser.objects.get(username='testuser1'),
                updated_datetime = timezone.now(),
            )
            useritem_obj.save()

        userlist5 = UserList.objects.get(title='ToDoThings')
        text_list = ['wash cat', 'clean dog', 'make everything great', 'destroy the world', 'get the pizza']
        for cur_text_numb in range(5):
            useritem_obj = UserItem.objects.create(
                related_userlist = userlist5,
                text = text_list[cur_text_numb],
                status = 'done',
                last_update_author = CustomUser.objects.get(username='testuser1'),
                updated_datetime = timezone.now(),
            )
            useritem_obj.save()
                    
        #setting up the permissions tables
        for cur_userlist in [userlist1, userlist2, userlist3]:
            userlistcustomuser_readwrite_obj = UserListCustomUser_ReadWrite.objects.create(
                customuser = CustomUser.objects.get(username='testuser2'),
                userlist = cur_userlist
            )
            userlistcustomuser_readwrite_obj.save()

        for cur_userlist in [userlist4, userlist5]:
            userlistcustomuser_readonly_obj = UserListCustomUser_ReadOnly.objects.create(
                customuser = CustomUser.objects.get(username='testuser2'),
                userlist = cur_userlist
            )
            userlistcustomuser_readonly_obj.save()

    def test_get_all_userlists_rightwork(self):
        user1 = CustomUser.objects.get(username='testuser1')
        userlists = get_all_userlists(user1.id)
        self.assertEqual(len(userlists["userlists_byauthor"]), 5)

        user2 = CustomUser.objects.get(username='testuser2')
        userlists = get_all_userlists(user2.id)
        self.assertEqual(len(userlists["userlists_byauthor"]), 0)
        self.assertEqual(len(userlists["userlists_readwrite"]), 3)
        self.assertEqual(len(userlists["userlists_readonly"]), 2)

        user3 = CustomUser.objects.get(username='testuser3')
        userlists = get_all_userlists(user3.id)
        self.assertEqual(
            len(userlists["userlists_byauthor"]) + 
            len(userlists["userlists_readwrite"]) + 
            len(userlists["userlists_readonly"])
            , 0)