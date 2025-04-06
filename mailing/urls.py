from django.urls import path

from mailing.apps import MailingConfig
from mailing.services import BlockSendingView, run_sending, UnblockSendingView
from mailing.views import HomePageView
from mailing.views import MailingRecipientCreateView, MailingRecipientListView, MailingRecipientDetailView, \
    MailingRecipientUpdateView, MailingRecipientDeleteView, AttemptListView
from mailing.views import MessageListView, MessageDetailView, MessageUpdateView, MessageDeleteView, MessageCreateView
from mailing.views import SendingCreateView, SendingDeleteView, SendingUpdateView, SendingListView, SendingDetailView

app_name = MailingConfig.name

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('sending/list', SendingListView.as_view(), name='sending_list'),
    path('sending/<int:pk>', SendingDetailView.as_view(), name='sending_detail'),
    path('sending/new/', SendingCreateView.as_view(), name='sending_create'),
    path('sending/<int:pk>/edit/', SendingUpdateView.as_view(), name='sending_edit'),
    path('sending/<int:pk>/delete/', SendingDeleteView.as_view(), name='sending_delete'),
    path('recipient/list', MailingRecipientListView.as_view(), name='recipient_list'),
    path('message/list', MessageListView.as_view(), name='message_list'),
    path('message/<int:pk>', MessageDetailView.as_view(), name='message_detail'),
    path('message/new/', MessageCreateView.as_view(), name='message_create'),
    path('message/<int:pk>/edit/', MessageUpdateView.as_view(), name='message_edit'),
    path('message/<int:pk>/delete/', MessageDeleteView.as_view(), name='message_delete'),
    path('recipient/list', MailingRecipientListView.as_view(), name='recipient_list'),
    path('recipient/<int:pk>', MailingRecipientDetailView.as_view(), name='recipient_detail'),
    path('recipient/new/', MailingRecipientCreateView.as_view(), name='recipient_create'),
    path('recipient/<int:pk>/edit/', MailingRecipientUpdateView.as_view(), name='recipient_edit'),
    path('recipient/<int:pk>/delete/', MailingRecipientDeleteView.as_view(), name='recipient_delete'),
    path('attempts/', AttemptListView.as_view(), name='attempts'),
    path('sending/<int:sending_id>/run/', run_sending, name='run_sending'),
    path('<int:sending_id>/block/', BlockSendingView.as_view(), name='block_sending'),
    path('<int:sending_id>/unblock/', UnblockSendingView.as_view(), name='unblock_sending'),
    # path('statistics/', statistics_view, name='statistics_view'),
    # path("block_sending/<int:pk>", block_mailing, name="block_mailing"),
    # path("<int:pk>/block", block_user, name="block_user")
]
