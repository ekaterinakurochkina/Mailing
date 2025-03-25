from django.views.generic.edit import DeleteView, CreateView, UpdateView
from django.views.generic import ListView, DetailView, TemplateView
from .forms import SendingForm, SendingModeratorForm, MessageForm, MailingRecipientForm
from .models import MailingRecipient, Message, Sending, MailingAttempt
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from mailing.service import get_object_from_cache
from django.forms import inlineformset_factory


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
            return get_object_from_cache()  # подключаем к представлению функцию обращения к кешу
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

    # def get_context_data(self, **kwargs):
    #     context_data = super().get_context_data()
    #     SendingFormset = inlineformset_factory(Sending, Message, MessageForm, extra=1)
    #     if self.request.method == "POST":
    #         context_data["formset"] = SendingFormset(self.request.POST, instance=self.object)
    #     else:
    #         context_data["formset"] = SendingFormset(instance=self.object)
    #     return context_data
    #
    # def form_valid(self, form):
    #     context_data = self.get_context_data()
    #     formset = context_data["formset"]
    #     if form.is_valid() and formset.is_valid():
    #         self.object = form.save()
    #         formset.instance = self.object
    #         formset.save()
    #         return super().form_valid(form)
    #     else:
    #         return self.render_to_response(self.get_context_data(form=form, formset=formset))

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
            return get_object_from_cache()  # подключаем к представлению функцию обращения к кешу
        else:
            return Message.objects.filter(owner=user)


class MessageDetailView(LoginRequiredMixin, DetailView):
    model = Message
    template_name = "message_detail.html"


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = "message_form.html"

    # def get_form_class(self):
    #     user = self.request.user
    #     if user == self.object.owner:
    #         return MessageForm
    #     # if user.has_perm("mailing.can_canceled_message"):
    #     #     return MessageModeratorForm
    #     raise PermissionDenied

    def get_success_url(self):
        return reverse_lazy('mailing:message_detail', kwargs={'pk': self.object.pk})


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = Message
    template_name = "message_confirm_delete.html"
    success_url = reverse_lazy("mailing:message_list")


# Виджеты для получателей рассылки ____________________________________________________________________________________

class MailingRecipientCreateView(LoginRequiredMixin, CreateView):
    model = MailingRecipient
    form_class = MailingRecipientForm
    # fields = ["name", 'recipient', 'message']
    template_name = "recipient_form.html"
    success_url = reverse_lazy("mailing:recipient_list")

    def form_valid(self, form):
        recipient = form.save()
        user = self.request.user
        recipient.owner = user
        recipient.save()
        return super().form_valid(form)


class MailingRecipientListView(LoginRequiredMixin, ListView):
    model = MailingRecipient
    template_name = "recipient_list.html"
    context_object_name = "recipients"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["unique_recipients"] = MailingRecipient.objects.distinct().count()
        return context


class MailingRecipientDetailView(LoginRequiredMixin, DetailView):
    model = MailingRecipient
    template_name = "recipient_detail.html"


class MailingRecipientUpdateView(LoginRequiredMixin, UpdateView):
    model = MailingRecipient
    form_class = MailingRecipientForm
    template_name = "recipient_form.html"

    def get_form_class(self):
        user = self.request.user
        if user == self.object.owner:
            return MailingRecipientForm
        # if user.has_perm("mailing.can_canceled_message"):
        #     return MessageModeratorForm
        raise PermissionDenied

    def get_success_url(self):
        return reverse_lazy('mailing:recipient_detail', kwargs={'pk': self.object.pk})


class MailingRecipientDeleteView(LoginRequiredMixin, DeleteView):
    model = MailingRecipient
    template_name = "recipient_confirm_delete.html"
    success_url = reverse_lazy("mailing:recipient_list")
