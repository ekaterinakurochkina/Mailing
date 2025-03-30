from django.urls import path
from users.apps import UsersConfig
from django.contrib.auth.views import LoginView, LogoutView
from users.views import logout_view, UserCreateView, UserDeleteView, UserListView, UserUpdateView

from django.contrib.auth.views import LoginView
from users.views import logout_view, UserCreateView
from users.views import logout_view
from users.services import block_user


from .views import UserCreateView

# app_name = 'users'
app_name = UsersConfig.name

urlpatterns = [
    path('login/', LoginView.as_view(template_name="login.html"), name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', UserCreateView.as_view(template_name="user_form.html"), name='register'),
    # path('users/email-confirm/<str:token>', email_verification, name='email-confirm'),
    path('users/list', UserListView.as_view(), name='user_list'),
    path('users/<int:pk>/delete/', UserDeleteView.as_view(), name='user_delete'),
    path('users/<int:pk>/edit/', UserUpdateView.as_view(), name='user_edit'),
    path("<int:pk>/block", block_user, name="block_user"),
]
# (template_name="user_form.html")
# login/
#  email_verification