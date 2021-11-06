from django.urls import path
from .views import StartPage, MainPage, DetailList

urlpatterns = [
    path('', StartPage.as_view(), name='startpage'),
    path('lists/new', MainPage.as_view(), name='mainpage'),
    path('lists/<int:userlist_id>', DetailList.as_view(), name='detailpage'),
    path('lists/', MainPage.as_view(), name='mainpage'),
]