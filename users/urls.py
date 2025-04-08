# from users.views import UserLogoutView
from django.contrib.auth.views import LoginView
from django.urls import path

from users.apps import UsersConfig
from users.views import UserCreateView, UserDeleteView, UserListView, UserUpdateView, email_verification
from users.views import logout_view, block_user, unblock_user

# app_name = 'users'
app_name = UsersConfig.name

urlpatterns = [
    path('login/', LoginView.as_view(template_name="login.html"), name='login'),
    path('logout/', logout_view, name='logout'),
    # path('logout/', UserLogoutView.as_view(), name='logout'),
    path('register/', UserCreateView.as_view(template_name="user_form.html"), name='register'),
    path('email-confirm/<str:token>/', email_verification, name='email-confirm'),
    path('users/list', UserListView.as_view(), name='user_list'),
    path('users/<int:pk>/delete/', UserDeleteView.as_view(), name='user_delete'),
    path('<int:pk>/edit/', UserUpdateView.as_view(), name='user_edit'),
    # path("<int:pk>/edit/", InactivateUser.as_view(), name="block_user"),
    path("<int:pk>/block", block_user, name="block_user"),
    path("<int:pk>/unblock", unblock_user, name="unblock_user"),
]
# (template_name="user_form.html")
# login/
#  email_verification
