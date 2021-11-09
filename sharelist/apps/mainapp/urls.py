from django.urls import path
from .views import (
    StartPage, MainPage, DetailList, CreateList, DeleteList, ShareListConfirm,
    RemoveList, UserListControl
)

urlpatterns = [
    path('', StartPage.as_view(), name='startpage'),
    path('lists/new', CreateList.as_view(), name='newlist'),
    path('lists/<int:userlist_id>', DetailList.as_view(), name='detailpage'),
    path('lists/<int:userlist_id>/remove', RemoveList.as_view(), name='removelist'),
    path('lists/<int:userlist_id>/delete', DeleteList.as_view(), name='deletelist'),
    path('lists/<int:userlist_id>/control', UserListControl.as_view(), name='controllist'),
    path('lists/<int:userlist_id>/<str:sharecode>', ShareListConfirm.as_view(), name='sharepage'),
    path('lists/', MainPage.as_view(), name='mainpage'),
]