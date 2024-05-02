from django.urls import path
from .views import home, redirect_uri, groups, group_detail, remove_users, add_users, remove_user, add_user, users_list, logout_custom, redirect_uri_automatic

urlpatterns = [
    path('logout_custom/',logout_custom, name="logout_custom"),
    path('',home, name="home_url"),
    path('redirect_uri/',redirect_uri),
    path('redirect_uri_automatic/',redirect_uri_automatic, name="redirect_uri_automatic"),
    path('groups/',groups, name="groups"),
    path('group/<str:id>/',group_detail, name="group_detail"),
    path('group/<str:id>/remove_users',remove_users, name="remove_users"),
    path('group/<str:group_id>/remove_user/<str:user_id>',remove_user, name="remove_user"),
    path('group/<str:id>/add_users',add_users, name="add_users"),
    path('group/<str:group_id>/add_user/<str:user_id>',add_user, name="add_user"),
    path('group/<str:id>/users_list',users_list, name="users_list"),
]