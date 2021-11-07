from django.urls import path
from .views import (
    StartPage, MainPage, DetailList, CreateList, DeleteList, ShareList,
)

urlpatterns = [
    path('', StartPage.as_view(), name='startpage'),
    path('lists/new', CreateList.as_view(), name='newlist'),
    path('lists/<int:userlist_id>', DetailList.as_view(), name='detailpage'),
    path('lists/<int:userlist_id>/delete', DeleteList.as_view(), name='deletelist'),
    path('lists/<int:userlist_id>/<str:sharecode>', ShareList.as_view(), name='sharepage'),
    path('lists/', MainPage.as_view(), name='mainpage'),
]