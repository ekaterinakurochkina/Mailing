from django.urls import path
from mailing.apps import MailingConfig
from mailing.views import HomePageView
from mailing.views import SendingCreateView, SendingDeleteView, SendingUpdateView,SendingListView, SendingDetailView
from mailing.views import MessageListView, MessageDetailView, MessageUpdateView, MessageDeleteView, MessageCreateView

app_name = MailingConfig.name


urlpatterns = [
    path('',HomePageView.as_view(), name='home'),
    path('sending/list',SendingListView.as_view(), name='sending_list'),
    path('sending/<int:pk>',SendingDetailView.as_view(), name='sending_detail'),
    path('sending/new/',SendingCreateView.as_view(), name='sending_create'),
    path('sending/<int:pk>/edit/',SendingUpdateView.as_view(), name='sending_edit'),
    path('sending/<int:pk>/delete/',SendingDeleteView.as_view(), name='sending_delete'),
    path('recipient/list',SendingListView.as_view(), name='recipient_list'),
    path('message/list',MessageListView.as_view(), name='message_list'),
    path('message/<int:pk>',MessageDetailView.as_view(), name='message_detail'),
    path('message/new/',MessageCreateView.as_view(), name='message_create'),
    path('message/<int:pk>/edit/',MessageUpdateView.as_view(), name='message_edit'),
    path('message/<int:pk>/delete/',MessageDeleteView.as_view(), name='message_delete'),
]

