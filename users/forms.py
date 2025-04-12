from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm

from mailing.forms import StyleFormMixin
from .models import User


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
