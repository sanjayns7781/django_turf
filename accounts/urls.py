from django.urls import path
from .views import register,login,get_profile,list_users,manage_user

urlpatterns = [
    path('register/',register),
    path('login/',login),
    path('profile/',get_profile),
    path("users/", list_users, name="list_users"),
    path('users/<int:user_id>',manage_user,name="manage_user")
]
