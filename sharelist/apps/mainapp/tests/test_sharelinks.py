from django.test import TestCase
from accounts.models import CustomUser
from mainapp.models import UserList, ItemList, UserListCustomUser_ReadOnly, UserListCustomUser_ReadWrite
from mainapp.permissions_logic import add_permission_readonly
from django.utils import timezone

class TestClassModelsCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        print("setUpTestData: Run once to set up non-modified data for all class methods.")
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


        listtitles = ['First', 'Second']
        for cur_list_numb in range(len(listtitles)):
            userlist_obj = UserList.objects.create_userlist(
                title = f'{listtitles[cur_list_numb]}',
                author = CustomUser.objects.get(username='testuser1'),
                description = f'This is {cur_list_numb} testlist, using for test the lists',
                created_datetime = timezone.now(),
                updated_datetime = timezone.now(),
                last_update_author = CustomUser.objects.get(username='testuser1'),
                is_public = False,
                #sharelink_readwrite = 'IN_CONSTRUCTION',
                #sharelink_readonly = 'IN_CONSTRUCTION',
            )
            userlist_obj.save()

        userlist1 = UserList.objects.get(title='First')
        # text_list = ['123', '456', '789']
        # for cur_text_numb in range(3):
        #     itemlist_obj = ItemList.objects.create(
        #         related_userlist = userlist1,
        #         text = text_list[cur_text_numb],
        #         status = 'done',
        #         last_update_author = CustomUser.objects.get(username='testuser2'),
        #         updated_datetime = timezone.now(),
        #     )
        #     itemlist_obj.save()

        #setting up the permissions tables
        for cur_userlist in [userlist1]:
            userlistcustomuser_readonly_obj = UserListCustomUser_ReadOnly.objects.create(
                customuser = CustomUser.objects.get(username='testuser2'),
                userlist = cur_userlist
            )
            userlistcustomuser_readonly_obj.save()
    

    def test_UserListCustomUser_ReadOnly_listnotfound(self):
        try:
            add_permission_readonly(userlist_id=3, user_id=2, sharelink="QGRPgaRr3-uhfjWQ")
            self.assertTrue(False)
        except LookupError:
            self.assertTrue(True)

    def test_UserListCustomUser_ReadOnly_wrongsharelink(self):
        userlist2 = UserList.objects.get(title='Second')
        right_sharelink = userlist2.sharelink_readonly
        wrong_sharelink = right_sharelink.swapcase()
        if right_sharelink == wrong_sharelink:
            #this is very unique sutiation. Congratz!
            wrong_sharelink = 'AAAAAAAAAAAAAAAA'
        #print(f'right: {right_sharelink}, wrong: {wrong_sharelink}')
        try:
            add_permission_readonly(userlist_id=2, user_id=2, sharelink=wrong_sharelink)
            self.assertTrue(False)
        except ValueError:
            self.assertTrue(True)
        
    def test_UserListCustomUser_ReadOnly_AlredyExistException(self):
        userlist2 = UserList.objects.get(title='Second')
        right_sharelink = userlist2.sharelink_readonly
        try:
            add_permission_readonly(userlist_id=1, user_id=2, sharelink=right_sharelink)
            self.assertTrue(False)
        except ValueError:
            self.assertTrue(True)

    def test_UserListCustomUser_ReadOnly_rightwork(self):
        userlist2 = UserList.objects.get(title='Second')
        right_sharelink = userlist2.sharelink_readonly
        try:
            add_permission_readonly(userlist_id=2, user_id=2, sharelink=right_sharelink)
            self.assertTrue(True)    
        except (ValueError, LookupError):
            self.assertTrue(False)
        UserListCustomUser_ReadOnly.objects.get(customuser=2, userlist=2)