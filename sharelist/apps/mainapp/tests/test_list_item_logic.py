from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import (
    ObjectDoesNotExist, PermissionDenied,
    ValidationError)
from django.test import Client
from django.test.client import RequestFactory
from django.db import IntegrityError

from accounts.models import CustomUser
from mainapp.models import (
    UserList,
    UserItem,
    UserListCustomUser_ReadOnly,
    UserListCustomUser_ReadWrite
)
from mainapp.forms import UserListForm, UserItemForm
from mainapp.services.list_item_logic import (
    get_all_userlists, get_userlist_detail_maininfo,
    get_userlist_detail_items, get_userlist_detail_context,
    save_userlist_detail_maininfo, save_userlist_detail_items)



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
                description = f'This is {cur_list_numb + 1} testlist, using for test the lists',
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

    def test_get_userlist_detail_maininfo(self):
        user1 = CustomUser.objects.get(username='testuser1')
        userlist2 = UserList.objects.get(title='Second')

        #userlist Exist failes
        try:
            form = get_userlist_detail_maininfo(user1.id, 99999999)
            self.assertTrue(False, msg="Userlist 99999999 doesnt exist, but \
            function returned something?")
        except ObjectDoesNotExist:
            self.assertTrue(True)

        #no access
        user3 = CustomUser.objects.get(username='testuser3')
        try:
            form = get_userlist_detail_maininfo(user3.id, userlist2.id)
            self.assertTrue(False, msg="User should not get access to this \
            userlist, but he is")
        except PermissionDenied:
            self.assertTrue(True)
        
        #proper work
        form = get_userlist_detail_maininfo(user1.id, userlist2.id)
        self.assertEqual(
            form.initial['title'],
            'Second'
        )
        self.assertEqual(
            form.initial['description'],
            'This is 2 testlist, using for test the lists'
        )

    def test_get_userlist_detail_items(self):
        user1 = CustomUser.objects.get(username='testuser1')
        userlist2 = UserList.objects.get(title='Second')

        #proper work
        formset = get_userlist_detail_items(user1.id, userlist2.id)
        self.assertEqual(
            formset[0].initial['text'],
            '123'
        )
        self.assertEqual(
            formset[2].initial['text'],
            '789'
        )

    def test_get_userlist_detail_context(self):
        user1 = CustomUser.objects.get(username='testuser1')
        userlist2 = UserList.objects.get(title='Second')
        context = get_userlist_detail_context(user1.id, userlist2.id)
        self.assertEqual(
            type(context['userlist_form']),
            UserListForm
        )
        self.assertEqual(
            context['item_formset'][2].initial['text'],
            '789'
        )

    def test_save_userlist_detail_maininfo(self):
        user1 = CustomUser.objects.get(username='testuser1')
        userlist3 = UserList.objects.get(title='Third')
        factory = RequestFactory()
        request = factory.post('', {'title': 'POST123', 'description': 'TEST_DESC'})
        request.user = user1
        try:
            form = save_userlist_detail_maininfo(request, userlist3.id)
            self.assertEqual(form.cleaned_data.get('title'), 'POST123')
            self.assertEqual(form.cleaned_data.get('description'), 'TEST_DESC')
            
        except ValidationError:
            self.assertTrue(False, msg='Didnt saved userlist_detail_maininfo!')

        #update userlist info for test function
        userlist3 = UserList.objects.get(id=userlist3.id)

        self.assertEqual(userlist3.title, 'POST123')
        self.assertEqual(userlist3.description, 'TEST_DESC')

    def test_save_userlist_detail_items(self):
        user1 = CustomUser.objects.get(username='testuser1')
        userlist = UserList.objects.get(title='Third')
        factory = RequestFactory()
        data = {
            'form-TOTAL_FORMS': '2',
            'form-INITIAL_FORMS': '5',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-text': 'A',
            'form-0-status': 'done',
            'form-1-text': 'B',
            'form-1-status': 'in_progress',
        }
        request = factory.post('', data)
        request.user = user1
        try:
            item_formset = save_userlist_detail_items(request, userlist.id)
            self.assertEqual(item_formset[0].cleaned_data.get('text'), 'A')
            self.assertEqual(item_formset[1].cleaned_data.get('status'), 'in_progress')
        except IntegrityError:
            self.assertTrue(False, msg='Transaction failed')
        
        #check item in database check
        useritem_obj = UserItem.objects.filter(
            related_userlist=userlist.id
        ).order_by('text')[0]
        self.assertEqual(useritem_obj.text, 'A')
        self.assertEqual(useritem_obj.status, 'done')
        