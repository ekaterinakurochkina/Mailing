from django.urls import path
from users.apps import UsersConfig
from django.contrib.auth.views import LoginView, LogoutView
from users.views import logout_view, UserCreateView, email_verification, UserDeleteView, UserListView

from django.contrib.auth.views import LoginView
from users.views import logout_view, UserCreateView, email_verification
from users.views import logout_view


from .views import UserCreateView

# app_name = 'users'
app_name = UsersConfig.name

urlpatterns = [
    path('login/', LoginView.as_view(template_name="login.html"), name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', UserCreateView.as_view, name='register'),
    path('users/email-confirm/<str:token>', email_verification, name='email-confirm'),
    path('users/list', UserListView.as_view(), name='user_list'),
    path('users/<int:pk>/delete/', UserDeleteView.as_view(), name='user_delete'),
]
# (template_name="user_form.html")
# login/
