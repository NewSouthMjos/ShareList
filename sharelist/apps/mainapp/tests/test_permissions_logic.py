from django.test import TestCase
from accounts.models import CustomUser
from mainapp.models import UserList, UserListCustomUser_ReadOnly, UserListCustomUser_ReadWrite
from mainapp.services.permissions_logic import add_permission, detele_permission, set_permission, PermissionAlreadyGranted, userlist_access_check
from django.utils import timezone
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist


class TestPermissionsLogicCase(TestCase):

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
        
        userlistcustomuser_readwrite_obj = UserListCustomUser_ReadWrite.objects.create(
            customuser = CustomUser.objects.get(username='testuser3'),
            userlist = userlist1
        )
        userlistcustomuser_readwrite_obj.save()

    def test_userlist_access_check(self):
        user1 = CustomUser.objects.get(username='testuser1')
        user2 = CustomUser.objects.get(username='testuser2')
        user3 = CustomUser.objects.get(username='testuser3')
        userlist1 = UserList.objects.get(title='First')
        userlist2 = UserList.objects.get(title='Second')

        #author rights
        self.assertEqual(
            userlist_access_check(user1.id, userlist1.id), 3
        )

        #readwrite rights
        self.assertEqual(
            userlist_access_check(user3.id, userlist1.id), 2
        )

        #readonly rights
        self.assertEqual(
            userlist_access_check(user2.id, userlist1.id), 1
        )

        #no access
        self.assertEqual(
            userlist_access_check(user3.id, userlist2.id), 0
        )

    def test_UserListCustomUser_ReadOnly_listnotfound(self):
        user = CustomUser.objects.get(username="testuser2")
        try:
            add_permission(userlist_id=765076763, user_id=user.id, sharelink="QGRPgaRr3-uhfjWQ", mode="readonly")
            self.assertTrue(False)
        except ObjectDoesNotExist as error:
            self.assertTrue(True, msg=error.args)

    def test_UserListCustomUser_ReadOnly_wrong_sharelink(self):
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
        
    def test_UserListCustomUser_ReadOnly_already_exist_exception(self):
        userlist1 = UserList.objects.get(title='First')
        user = CustomUser.objects.get(username="testuser2")
        right_sharelink = userlist1.sharelink_readonly
        try:
            add_permission(userlist_id=userlist1.id, user_id=user.id, sharelink=right_sharelink, mode="readonly")
            self.assertTrue(False)
        except PermissionAlreadyGranted as error:
            self.assertTrue(True, msg=error.args)

    def test_UserListCustomUser_ReadOnly_wrongcode(self):
        userlist2 = UserList.objects.get(title='Second')
        user = CustomUser.objects.get(username="testuser2")
        right_sharelink = userlist2.sharelink_readonly
        try:
            add_permission(userlist_id=userlist2.id, user_id=user.id, sharelink=right_sharelink, mode="readonlywrite")
            self.assertTrue(False)
        except ValueError as error:
            self.assertTrue(True, msg=error.args)

    def test_UserListCustomUser_ReadOnly_already_can_readwrite(self):
        userlist1 = UserList.objects.get(title='First')
        user = CustomUser.objects.get(username="testuser3")
        right_sharelink = userlist1.sharelink_readonly
        try:
            add_permission(userlist_id=userlist1.id, user_id=user.id, sharelink=right_sharelink, mode="readonly")
            self.assertTrue(False)
        except PermissionAlreadyGranted as error:
            self.assertTrue(True, msg=error.args)

    def test_UserListCustomUser_ReadOnly_rightwork(self):
        userlist2 = UserList.objects.get(title='Second')
        user = CustomUser.objects.get(username="testuser2")
        right_sharelink = userlist2.sharelink_readonly
        try:
            add_permission(userlist_id=userlist2.id, user_id=user.id, sharelink=right_sharelink, mode="readonly")
            self.assertTrue(True)    
        except (ValueError, LookupError, ObjectDoesNotExist) as error:
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
        except (ValueError, LookupError, ObjectDoesNotExist) as error:
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
        except (ValueError, ObjectDoesNotExist) as error:
            self.assertTrue(True)

        #wrong mode passed
        try:
            detele_permission(userlist_id=userlist1.id, acting_user_id=user_act.id, user_id=user.id, mode="readonlywrite")
            self.assertTrue(False, msg="wrong mode passed, but deleted?")
        except (ValueError, LookupError) as error:
            self.assertTrue(True)

        user3 = CustomUser.objects.get(username="testuser3")
        #no access
        try:
            detele_permission(userlist_id=userlist1.id, acting_user_id=user3.id, user_id=user.id, mode="readonly")
            self.assertTrue(False, msg="wrong author passed and \
            user is not accesseble to delete permission, but deleted?")
        except (ValueError, LookupError, PermissionDenied) as error:
            self.assertTrue(True)
        
        #rightwork
        try:
            detele_permission(userlist_id=userlist1.id, acting_user_id=user_act.id, user_id=user.id, mode="readonly")
            self.assertTrue(True)
        except (ValueError, LookupError) as error:
            self.assertTrue(False, msg=error.args)

    def test_set_permissions_errors(self):
        userlist2 = UserList.objects.get(title='Second')
        acting_user = CustomUser.objects.get(username="testuser1")
        user = CustomUser.objects.get(username="testuser2")

        #wrong author
        try:
            set_permission(userlist_id=userlist2.id, acting_user_id=user.id, user_id=user.id, mode="none")
            self.assertTrue(False, msg="Wrong author can sets permissions for list?")
        except PermissionDenied as error:
            self.assertTrue(True)

        #wrong list
        try:
            set_permission(userlist_id=34532342, acting_user_id=acting_user.id, user_id=user.id, mode="none")
            self.assertTrue(False, msg="Wrong user passed, but no errors?")
        except ObjectDoesNotExist as error:
            self.assertTrue(True)

        #wrong mode passed
        try:
            set_permission(userlist_id=userlist2.id, acting_user_id=acting_user.id, user_id=user.id, mode="readwriteonly")
            self.assertTrue(False, msg="Wrong mode passed, but no errors?")
        except ValueError as error:
            self.assertTrue(True)

        #wrong user passed
        try:
            set_permission(userlist_id=userlist2.id, acting_user_id=acting_user.id, user_id=34532342, mode="readwrite")
            self.assertTrue(False, msg="Wround user id passed, but no errors?")
        except (ValueError, LookupError, ObjectDoesNotExist) as error:
            self.assertTrue(True)
            

    def test_set_permissions_none(self):
        userlist2 = UserList.objects.get(title='Second')
        acting_user = CustomUser.objects.get(username="testuser1")
        user = CustomUser.objects.get(username="testuser2")

        try:
            set_permission(userlist_id=userlist2.id, acting_user_id=acting_user.id, user_id=user.id, mode="none")
        except (ValueError, LookupError, ObjectDoesNotExist) as error:
            self.assertTrue(False, msg="Permissions didnt setted. Permissions_logic error: " + str(error.args))
        jointable_record = UserListCustomUser_ReadOnly.objects.filter(customuser=user.id, userlist=userlist2.id)
        if len(jointable_record) >= 1:
            self.assertTrue(False, msg="Somewhy permissions are already there in R jointable (should be deleted)")
        jointable_record = UserListCustomUser_ReadWrite.objects.filter(customuser=user.id, userlist=userlist2.id)
        if len(jointable_record) >= 1:
            self.assertTrue(False, msg="Somewhy permissions are already there in RW jointable (should be deleted)")

    def test_set_permissions_readonly(self):
        userlist2 = UserList.objects.get(title='Second')
        acting_user = CustomUser.objects.get(username="testuser1")
        user = CustomUser.objects.get(username="testuser2")

        try:
            set_permission(userlist_id=userlist2.id, acting_user_id=acting_user.id, user_id=user.id, mode="readonly")
        except (ValueError, LookupError, ObjectDoesNotExist) as error:
            self.assertTrue(False, msg="Permissions didnt setted. Permissions_logic error: " + str(error.args))
        jointable_record = UserListCustomUser_ReadOnly.objects.filter(customuser=user.id, userlist=userlist2.id)
        if len(jointable_record) != 1:
            self.assertTrue(False, msg="Somewhy permissions are NOT there, but shoulde be")
        jointable_record = UserListCustomUser_ReadWrite.objects.filter(customuser=user.id, userlist=userlist2.id)
        if len(jointable_record) >= 1:
            self.assertTrue(False, msg="Somewhy permissions are already there in RW jointable (should be deleted)")

        #adding same permission for 2th time should case error:
        try:
            set_permission(userlist_id=userlist2.id, acting_user_id=acting_user.id, user_id=user.id, mode="readonly")
        except PermissionAlreadyGranted as error:
            self.assertTrue(True)

    def test_set_permissions_readwrite(self):
        userlist2 = UserList.objects.get(title='Second')
        acting_user = CustomUser.objects.get(username="testuser1")
        user = CustomUser.objects.get(username="testuser2")

        try:
            set_permission(userlist_id=userlist2.id, acting_user_id=acting_user.id, user_id=user.id, mode="readwrite")
        except (ValueError, LookupError, ObjectDoesNotExist, PermissionAlreadyGranted) as error:
            self.assertTrue(False, msg="Permissions didnt setted. Permissions_logic error: " + str(error.args))
        jointable_record = UserListCustomUser_ReadOnly.objects.filter(customuser=user, userlist=userlist2)
        if len(jointable_record) >= 1:
            self.assertTrue(False, msg="Somewhy permissions are already there in R jointable (should be deleted)")
        jointable_record = UserListCustomUser_ReadWrite.objects.filter(customuser=user, userlist=userlist2)
        if len(jointable_record) != 1:
            self.assertTrue(False, msg="Somewhy permissions are NOT there, but should be")
