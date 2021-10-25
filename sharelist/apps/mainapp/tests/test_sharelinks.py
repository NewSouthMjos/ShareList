from django.test import TestCase
from accounts.models import CustomUser
from mainapp.models import UserList, ItemList, UserListCustomUser_ReadOnly, UserListCustomUser_ReadWrite
from mainapp.services.permissions_logic import add_permission, detele_permission
from django.utils import timezone


class TestClassModelsCase(TestCase):

    #@classmethod
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

        listtitles = ['First', 'Second']
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

        #setting up the permissions tables
        for cur_userlist in [userlist1]:
            userlistcustomuser_readonly_obj = UserListCustomUser_ReadOnly.objects.create(
                customuser = CustomUser.objects.get(username='testuser2'),
                userlist = cur_userlist
            )
            userlistcustomuser_readonly_obj.save()

    def test_UserListCustomUser_ReadOnly_listnotfound(self):
        user = CustomUser.objects.get(username="testuser2")
        try:
            add_permission(userlist_id=765076763, user_id=user.id, sharelink="QGRPgaRr3-uhfjWQ", mode="readonly")
            self.assertTrue(False)
        except LookupError as error:
            self.assertTrue(True, msg=error.args)

    def test_UserListCustomUser_ReadOnly_wrongsharelink(self):
        userlist2 = UserList.objects.get(title='Second')
        user = CustomUser.objects.get(username="testuser2")
        right_sharelink = userlist2.sharelink_readonly
        wrong_sharelink = right_sharelink.swapcase()
        if right_sharelink == wrong_sharelink:
            #this is so unique sutiation. Congratz!
            wrong_sharelink = 'AAAAAAAAAAAAAAAA'
        try:
            add_permission(userlist_id=userlist2.id, user_id=user.id, sharelink=wrong_sharelink, mode="readonly")
            self.assertTrue(False)
        except ValueError as error:
            self.assertTrue(True, msg=error.args)
        
    def test_UserListCustomUser_ReadOnly_AlredyExistException(self):
        userlist1 = UserList.objects.get(title='First')
        user = CustomUser.objects.get(username="testuser2")
        right_sharelink = userlist1.sharelink_readonly
        try:
            add_permission(userlist_id=userlist1.id, user_id=user.id, sharelink=right_sharelink, mode="readonly")
            self.assertTrue(False)
        except ValueError as error:
            self.assertTrue(True, msg=error.args)

    def test_UserListCustomUser_ReadOnly_rightwork(self):
        userlist2 = UserList.objects.get(title='Second')
        user = CustomUser.objects.get(username="testuser2")
        right_sharelink = userlist2.sharelink_readonly
        try:
            add_permission(userlist_id=userlist2.id, user_id=user.id, sharelink=right_sharelink, mode="readonly")
            self.assertTrue(True)    
        except (ValueError, LookupError) as error:
            self.assertTrue(False, msg=error.args)
        try:
            UserListCustomUser_ReadOnly.objects.get(customuser=user.id, userlist=userlist2.id)
            self.assertTrue(True)
        except UserListCustomUser_ReadOnly.DoesNotExist:
            self.assertTrue(False, "Record didnt added to jointable")

    def test_UserListCustomUser_ReadWrite_rightwork(self):
        userlist2 = UserList.objects.get(title='Second')
        user = CustomUser.objects.get(username="testuser2")
        right_sharelink = userlist2.sharelink_readwrite
        try:
            add_permission(userlist_id=userlist2.id, user_id=user.id, sharelink=right_sharelink, mode="readwrite")
            self.assertTrue(True)    
        except (ValueError, LookupError) as error:
            self.assertTrue(False, msg=error.args)
        try:
            UserListCustomUser_ReadWrite.objects.get(customuser=user.id, userlist=userlist2.id)
            self.assertTrue(True)
        except UserListCustomUser_ReadWrite.DoesNotExist:
            self.assertTrue(False, "Record didnt added to jointable")

    def test_UserListCustomUser_ReadOnly_detele_permission(self):
        #list doesnt exist
        userlist1 = UserList.objects.get(title='First')
        user_act = CustomUser.objects.get(username="testuser1")
        user = CustomUser.objects.get(username="testuser2")
        try:
            detele_permission(userlist_id=765076763, acting_user_id=user_act.id, user_id=user.id, mode="readonly")
            self.assertTrue(False, msg="list doesnt exist, but deleted?")
        except (ValueError, LookupError) as error:
            self.assertTrue(True)

        #wrong mode passed
        try:
            detele_permission(userlist_id=userlist1.id, acting_user_id=user_act.id, user_id=user.id, mode="readonlywrite")
            self.assertTrue(False, msg="wrong mode passed, but deleted?")
        except (ValueError, LookupError) as error:
            self.assertTrue(True)

        #wrong author
        try:
            detele_permission(userlist_id=userlist1.id, acting_user_id=user.id, user_id=user.id, mode="readonly")
            self.assertTrue(False, msg="wrong author passed, but deleted?")
        except (ValueError, LookupError) as error:
            self.assertTrue(True)
        
        #rightwork
        try:
            detele_permission(userlist_id=userlist1.id, acting_user_id=user_act.id, user_id=user.id, mode="readonly")
            self.assertTrue(True)
        except (ValueError, LookupError) as error:
            self.assertTrue(False, msg=error.args)