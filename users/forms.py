from django import forms
from .models import User
from django.contrib.auth.forms import UserCreationForm
from mailing.forms import StyleFormMixin

from django.core.exceptions import ValidationError


class UserRegisterForm(StyleFormMixin, UserCreationForm):
    class Meta:
        model = User
        fields = ("email", "password1", "password2")

