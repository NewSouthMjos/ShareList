from django.test import TestCase
from accounts.models import CustomUser
from mainapp.models import UserList, ItemList, UserListCustomUser_ReadOnly, UserListCustomUser_ReadWrite
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


        listtitles = ['First', 'Second', 'Third', 'MyJobs', 'ToDoThings']
        for cur_list_numb in range(5):
            userlist_obj = UserList.objects.create(
                title = f'{listtitles[cur_list_numb]}',
                author = CustomUser.objects.get(username='testuser1'),
                description = f'This is {cur_list_numb} testlist, using for test the lists',
                created_datetime = timezone.now(),
                updated_datetime = timezone.now(),
                last_update_author = CustomUser.objects.get(username='testuser1'),
                is_public = False,
                sharelink_readwrite = 'IN_CONSTRUCTION',
                sharelink_readonly = 'IN_CONSTRUCTION',
            )
            userlist_obj.save()

        userlist1 = UserList.objects.get(title='First')

        userlist2 = UserList.objects.get(title='Second')
        text_list = ['123', '456', '789']
        for cur_text_numb in range(3):
            itemlist_obj = ItemList.objects.create(
                related_userlist = userlist2,
                text = text_list[cur_text_numb],
                status = 'done',
                last_update_author = CustomUser.objects.get(username='testuser2'),
                updated_datetime = timezone.now(),
            )
            itemlist_obj.save()

        userlist3 = UserList.objects.get(title='Third')
        text_list = ['foo_1', 'foo_2', 'foo_3']
        for cur_text_numb in range(3):
            itemlist_obj = ItemList.objects.create(
                related_userlist = userlist3,
                text = text_list[cur_text_numb],
                status = 'in_progess',
                last_update_author = CustomUser.objects.get(username='testuser1'),
                updated_datetime = timezone.now(),
            )
            itemlist_obj.save()


        userlist4 = UserList.objects.get(title='MyJobs')
        text_list = ['translator', 'doctor', 'driver']
        for cur_text_numb in range(3):
            itemlist_obj = ItemList.objects.create(
                related_userlist = userlist4,
                text = text_list[cur_text_numb],
                status = 'not_done',
                last_update_author = CustomUser.objects.get(username='testuser1'),
                updated_datetime = timezone.now(),
            )
            itemlist_obj.save()

        userlist5 = UserList.objects.get(title='ToDoThings')
        text_list = ['wash cat', 'clean dog', 'make everything great', 'destroy the world', 'get the pizza']
        for cur_text_numb in range(5):
            itemlist_obj = ItemList.objects.create(
                related_userlist = userlist5,
                text = text_list[cur_text_numb],
                status = 'done',
                last_update_author = CustomUser.objects.get(username='testuser1'),
                updated_datetime = timezone.now(),
            )
            itemlist_obj.save()

        

        #setting up the permissions tables
        for cur_userlist in [userlist1, userlist2, userlist3]:
            userlistcustomuser_readwrite_obj = UserListCustomUser_ReadWrite.objects.create(
                customuser = CustomUser.objects.get(username='testuser2'),
                userlist = cur_userlist
            )
            userlistcustomuser_readwrite_obj.save()

    def setUp(self):
        #print("setUp: Run once for every test method to setup clean data.")
        pass

    def test_userlist_title(self):
        userlist1 = UserList.objects.get(id=1)
        userlist1_title = userlist1.title
        self.assertEqual('First', userlist1_title)

    def test_userlist_author_username(self):
        userlist2 = UserList.objects.get(id=2)
        userlist2_author_username = userlist2.author.username
        self.assertEqual('testuser1', userlist2_author_username)

    def test_items_in_userlist(self):
        userlist = UserList.objects.get(title='ToDoThings')
        itemlist = list(ItemList.objects.filter(related_userlist=userlist))
        text = itemlist[0].text
        self.assertTrue('wash cat' == text)
        len_of_items = len(itemlist)
        self.assertEqual(5, len_of_items)

    def test_empty_list(self):
        userlist = UserList.objects.get(title='First')
        itemlist = list(ItemList.objects.filter(related_userlist=userlist))
        len_of_items = len(itemlist)
        self.assertEqual(0, len_of_items)

    def test_author(self):
        user1=CustomUser.objects.get(username='testuser1')
        userlist = list(UserList.objects.filter(author=user1))
        len_of_lists = len(userlist)
        self.assertEqual(5, len_of_lists)

    def test_UserListCustomUser_ReadWrite(self):
        user2=CustomUser.objects.get(username='testuser2')
        # jointable_records = UserListCustomUser_ReadWrite.objects.filter(customuser = user2)
        # userlist = list(UserList.objects.filter(
        #     userlistcustomuser_readwrite__in = jointable_records
        # ))
        userlist = list(UserList.objects.filter(
            userlistcustomuser_readwrite__in = UserListCustomUser_ReadWrite.objects.filter(customuser = user2)
        ))

        len_of_lists = len(userlist)
        self.assertEqual(3, len_of_lists)
