from django.urls import path
from .views import RegisterAPIView, LoginAPIView, UserListAPIView, UserDetailedAPIView, UserUpdateDeleteAPIView, LogDeletionView, SearchUserAPIView, BirthdayAPIView, SendingEmailToAllView

urlpatterns = [
    path('login',LoginAPIView.as_view()),
    path('signup',RegisterAPIView.as_view()),
    path('deleteuser/<int:id>', UserUpdateDeleteAPIView.as_view()),
    path('updateuser/<int:id>',UserUpdateDeleteAPIView.as_view()),
    path('getalluser',UserListAPIView.as_view()),
    path('getuser/<int:id>',UserDetailedAPIView.as_view()),
    path('deletelogs/<int:id>',LogDeletionView.as_view()),
    path('users/search/', SearchUserAPIView.as_view()),
    path('birthday-users/<int:id>',BirthdayAPIView.as_view()),
    path('send-birthday-emails',SendingEmailToAllView.as_view()),
]