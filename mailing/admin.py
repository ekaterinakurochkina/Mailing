from django.contrib import admin
from .models import MailingRecipient, Message, Sending, MailingAttempt


@admin.register(MailingRecipient)
class MailingRecipientAdmin(admin.ModelAdmin):
    list_display = ('email', 'name')
    list_filter = ('email', 'name',)
    search_fields = ('email', 'name',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id','subject', 'message_body')
    list_filter = ('subject', 'message_body',)
    search_fields = ('subject', 'message_body',)


@admin.register(Sending)
class SendingAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'owner')
    list_filter = ('id', 'status', 'owner', )
    search_fields = ('id', 'status', 'owner',)


@admin.register(MailingAttempt)
class MailingAttempt(admin.ModelAdmin):
    list_display = ('date_attempt', 'status_attempt', 'sending', 'answer')
    list_filter = ('date_attempt', 'status_attempt', 'sending',)
    search_fields = ('date_attempt', 'status_attempt', 'sending',)
