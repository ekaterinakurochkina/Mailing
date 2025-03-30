from django import forms
from django.urls import reverse_lazy
from django.forms import ModelForm
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm, UserCreationForm
from .models import User
from django.contrib.auth.forms import UserCreationForm
from mailing.forms import StyleFormMixin

from django.core.exceptions import ValidationError


class UserForm(StyleFormMixin, UserChangeForm):
    class Meta:
        model = User
        fields = (
            "email",
            "password",
            "phone",
            "description",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        phone = self.fields["phone"].widget

        self.fields["password"].widget = forms.HiddenInput()
        phone.attrs["class"] = "form-control bfh-phone"
        phone.attrs["data-format"] = "+7 (ddd) ddd-dd-dd"


class UserRegisterForm(StyleFormMixin, UserCreationForm):
    class Meta:
        model = User
        fields = ("email", "password1", "password2")
        # template_name = "user_form.html"


class UserUpdateForm(StyleFormMixin, ModelForm):
    class Meta:
        model = User
        fields = (
            "email",
            "password",
            "phone",
            "description",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        phone = self.fields["phone"].widget

        self.fields["password"].widget = forms.HiddenInput()
        phone.attrs["class"] = "form-control bfh-phone"
        phone.attrs["data-format"] = "+7 (ddd) ddd-dd-dd"


class PasswordRecoveryForm(StyleFormMixin, forms.Form):
    email = forms.EmailField(label="Укажите Email")


class UserLoginForm(StyleFormMixin, AuthenticationForm):
    model = User