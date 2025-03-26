from django.db.models import BooleanField
from django.forms import ModelForm
from .models import Sending, Message, MailingRecipient
from django.core.exceptions import ValidationError
from django.urls import reverse_lazy


class StyleFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field, BooleanField):
                field.widget.attrs['class'] = "form-check-input"
            else:
                field.widget.attrs["class"] = "form-control"
                field.widget.attrs["placeholder"] = field.label


class SendingForm(StyleFormMixin, ModelForm):
    class Meta:
        model = Sending
        fields = "__all__"
        # exclude = ("owner",)
        success_url = reverse_lazy("mailing:sending_list")

    # def create_owner(self):
    #     owner = self.request.user
    #     return owner


class SendingModeratorForm(StyleFormMixin, ModelForm):  # Класс для отображения сообщений для модератора
    class Meta:
        model = Sending
        fields = "__all__"


class MessageForm(StyleFormMixin, ModelForm):
    class Meta:
        model = Message
        fields = ['subject', 'message_body']
        success_url = reverse_lazy("mailing:message_list")


class MailingRecipientForm(StyleFormMixin, ModelForm):
    class Meta:
        model = MailingRecipient
        fields = ['email', 'name']
        success_url = reverse_lazy("mailing:recipient_list")
