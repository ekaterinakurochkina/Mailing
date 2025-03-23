from django.views.generic.edit import DeleteView, CreateView, UpdateView
from django.views.generic import ListView, DetailView, TemplateView
from .forms import SendingForm, SendingModeratorForm, MessageForm
from .models import MailingRecipient, Message, Sending, MailingAttempt
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from mailing.service import get_object_from_cache


class HomePageView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_sendings"] = Sending.objects.count()
        context["active_sendings"] = Sending.objects.filter(status="Запущена").count()
        context["unique_recipients"] = MailingRecipient.objects.distinct().count()
        return context


# Виджеты для рассылок ________________________________________________________________________________________________

class SendingCreateView(LoginRequiredMixin, CreateView):
    model = Sending
    form_class = SendingForm
    # fields = ["name", 'recipient', 'message']
    template_name = "sending_form.html"
    success_url = reverse_lazy("mailing:sending_list")

    def form_valid(self, form):
        sending = form.save()
        user = self.request.user
        sending.owner = user
        sending.save()
        return super().form_valid(form)


class SendingListView(LoginRequiredMixin, ListView):
    model = Sending
    template_name = "sending_list.html"
    context_object_name = "sendings"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_sendings"] = Sending.objects.count()
        context["active_sendings"] = Sending.objects.filter(status="Запущена").count()
        context["unique_recipients"] = MailingRecipient.objects.distinct().count()
        return context

    def get_queryset(self):
        user = self.request.user
        if user.has_perm("mailing.can_canceled_sending"):
            return get_object_from_cache()      # подключаем к представлению функцию обращения к кешу
        else:
            return Sending.objects.filter(owner=user)

class SendingDetailView(LoginRequiredMixin, DetailView):
    model = Sending
    template_name = "sending_detail.html"
#     надо дописать!

class SendingUpdateView(LoginRequiredMixin, UpdateView):
    model = Sending
    form_class = SendingForm
    template_name = "sending_form.html"

    def get_form_class(self):
        user = self.request.user
        if user == self.object.owner:
            return SendingForm
        if user.has_perm("mailing.can_canceled_sending"):
            return SendingModeratorForm
        raise PermissionDenied

    def get_success_url(self):
        return reverse_lazy('mailing:sending_detail', kwargs={'pk': self.object.pk})


class SendingDeleteView(LoginRequiredMixin, DeleteView):
    model = Sending
    template_name = "sending_confirm_delete.html"
    success_url = reverse_lazy("mailing:sending_list")


class AttemptListView(LoginRequiredMixin, ListView):
    template_name = "mailing_service/attempts.html"
    context_object_name = "attempt_list"

    def get_queryset(self):
        # Получаем только попытки рассылок, принадлежащих пользователю
        return MailingAttempt.objects.filter(mailing__created_by=self.request.user)


# Виджеты для сообщений _______________________________________________________________________________________________

class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    # fields = ["name", 'recipient', 'message']
    template_name = "message_form.html"
    success_url = reverse_lazy("mailing:message_list")

    def form_valid(self, form):
        message = form.save()
        user = self.request.user
        message.owner = user
        message.save()
        return super().form_valid(form)


class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = "message_list.html"
    context_object_name = "messages"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_мessages"] = Message.objects.count()
        context["unique_recipients"] = MailingRecipient.objects.distinct().count()
        return context

    def get_queryset(self):
        user = self.request.user
        if user.has_perm("mailing.can_canceled_message"):
            return get_object_from_cache()      # подключаем к представлению функцию обращения к кешу
        else:
            return Message.objects.filter(owner=user)

class MessageDetailView(LoginRequiredMixin, DetailView):
    model = Message
    template_name = "message_detail.html"


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = "message_form.html"

    def get_form_class(self):
        user = self.request.user
        if user == self.object.owner:
            return MessageForm
        # if user.has_perm("mailing.can_canceled_message"):
        #     return MessageModeratorForm
        raise PermissionDenied

    def get_success_url(self):
        return reverse_lazy('mailing:message_detail', kwargs={'pk': self.object.pk})


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = Message
    template_name = "message_confirm_delete.html"
    success_url = reverse_lazy("mailing:message_list")