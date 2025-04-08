

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic import View
from django.views.generic.edit import DeleteView, CreateView, UpdateView

from .forms import SendingForm, MessageForm, MailingRecipientForm
from .models import MailingRecipient, Message, Sending, MailingAttempt


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
    template_name = "sending_form.html"
    success_url = reverse_lazy("mailing:sending_list")

    def form_valid(self, form):
        sending = form.save()
        user = self.request.user
        sending.owner = user
        sending.save()
        return super().form_valid(form)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['recipient'].queryset = MailingRecipient.objects.filter(owner=self.request.user)
        form.fields['message'].queryset = Message.objects.filter(owner=self.request.user)
        return form


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

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset()
        if self.request.user.is_authenticated:
            if self.request.user.is_superuser or self.request.user.is_moderator:
                return qs
        return qs.filter(owner=self.request.user)


class SendingDetailView(LoginRequiredMixin, DetailView):
    model = Sending
    template_name = "sending_detail.html"


class SendingUpdateView(LoginRequiredMixin, UpdateView):
    model = Sending
    form_class = SendingForm
    template_name = "sending_form.html"

    def get_object(self, queryset=None):
        self.object = super().get_object(queryset)
        if self.object.owner != self.request.user and not self.request.user.is_superuser:
            raise PermissionDenied
        return self.object

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['recipient'].queryset = MailingRecipient.objects.filter(owner=self.request.user)
        form.fields['message'].queryset = Message.objects.filter(owner=self.request.user)
        return form

    def get_success_url(self):
        return reverse_lazy('mailing:sending_detail', kwargs={'pk': self.object.pk})


class SendingDeleteView(LoginRequiredMixin, DeleteView):
    model = Sending
    template_name = "sending_confirm_delete.html"
    success_url = reverse_lazy("mailing:sending_list")

    def get_object(self, queryset=None):
        self.object = super().get_object(queryset)
        if self.object.owner != self.request.user and not self.request.user.is_superuser:
            raise PermissionDenied
        return self.object


# Виджеты для попыток отправки сообщений ________________________________________________________________________________________
class AttemptListView(LoginRequiredMixin, ListView):
    model = MailingAttempt
    template_name = "attempts.html"
    context_object_name = "attempts"

    # def get_queryset(self):
    #     # Получаем только попытки рассылок, принадлежащих пользователю
    #     # return MailingAttempt.objects.filter(sending__created_by=self.request.user)
    #     return MailingAttempt.objects.all().order_by('-date_attempt')
    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset()
        if self.request.user.is_authenticated:
            if self.request.user.is_superuser or self.request.user.is_moderator:
                return qs
        return qs.filter(owner=self.request.user)


class AttemptCreateView(LoginRequiredMixin, CreateView):
    model = MailingAttempt
    template_name = "attempts.html"
    context_object_name = "attempts"

    def form_valid(self, form):
        recipient = form.save()
        recipient.owner = self.request.user
        recipient.save()
        return super().form_valid(form)


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
    success_url = reverse_lazy("mailing:message_list")

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset()
        if self.request.user.is_authenticated:
            if self.request.user.is_superuser or self.request.user.is_moderator:
                return qs
        return qs.filter(owner=self.request.user)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_мessages"] = Message.objects.count()
        context["unique_recipients"] = MailingRecipient.objects.distinct().count()
        context["мessage_id"] = Message.id
        return context


class MessageDetailView(LoginRequiredMixin, DetailView):
    model = Message
    template_name = "message_detail.html"
    context_object_name = "message"

    def get_object(self, queryset=None):
        self.object = super().get_object(queryset)
        if self.object.owner != self.request.user and not self.request.user.is_superuser:
            raise PermissionDenied
        return self.object


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = "message_form.html"

    def get_object(self, queryset=None):
        self.object = super().get_object(queryset)
        if self.object.owner != self.request.user and not self.request.user.is_superuser:
            raise PermissionDenied
        return self.object

    def get_success_url(self):
        return reverse_lazy('mailing:message_detail', kwargs={'pk': self.object.pk})


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = Message
    template_name = "message_confirm_delete.html"
    success_url = reverse_lazy("mailing:message_list")

    def get_object(self, queryset=None):
        self.object = super().get_object(queryset)
        if self.object.owner != self.request.user and not self.request.user.is_superuser:
            raise PermissionDenied
        return self.object


# Виджеты для получателей рассылки ____________________________________________________________________________________

class MailingRecipientCreateView(LoginRequiredMixin, CreateView):
    model = MailingRecipient
    fields = ["email", 'name', 'comment']
    template_name = "recipient_form.html"
    context_object_name = "recipient"
    success_url = reverse_lazy("mailing:recipient_list")

    def form_valid(self, form):
        recipient = form.save()
        user = self.request.user
        recipient.owner = user
        recipient.save()
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.groups.filter(name="Пользователь").exists() or self.request.user.is_superuser


class MailingRecipientListView(LoginRequiredMixin, ListView):
    model = MailingRecipient
    template_name = "recipient_list.html"
    context_object_name = "recipients"
    success_url = reverse_lazy("mailing:recipient_list")

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["unique_recipients"] = MailingRecipient.objects.distinct().count()
        return context

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset()
        if self.request.user.is_authenticated:
            if self.request.user.is_superuser or self.request.user.is_moderator:
                return qs
        return qs.filter(owner=self.request.user)


class MailingRecipientDetailView(LoginRequiredMixin, DetailView):
    model = MailingRecipient
    template_name = "recipient_detail.html"

    def get_object(self, queryset=None):
        self.object = super().get_object(queryset)
        if self.object.owner != self.request.user and not self.request.user.is_superuser:
            raise PermissionDenied
        return self.object


class MailingRecipientUpdateView(LoginRequiredMixin, UpdateView):
    model = MailingRecipient
    form_class = MailingRecipientForm
    template_name = "recipient_form.html"

    def get_object(self, queryset=None):
        self.object = super().get_object(queryset)
        if self.object.owner != self.request.user and not self.request.user.is_superuser:
            raise PermissionDenied
        return self.object

    def get_success_url(self):
        return reverse_lazy('mailing:recipient_detail', kwargs={'pk': self.object.pk})


class MailingRecipientDeleteView(LoginRequiredMixin, DeleteView):
    model = MailingRecipient
    template_name = "recipient_confirm_delete.html"
    success_url = reverse_lazy("mailing:recipient_list")

    def get_object(self, queryset=None):
        self.object = super().get_object(queryset)
        if self.object.owner != self.request.user and not self.request.user.is_superuser:
            raise PermissionDenied
        return self.object


# ____________________________
# def send_mail(mailing):
#     for recipient in mailing.recipients.all():
#         try:
#             send_mail(
#                 mailing.message.subject,
#                 mailing.message.message_body,
#                 'From-garden@yandex.ru',
#                 [recipient.email],
#             )
#             status = 'successfully'
#             response = 'Сообщение отправлено'
#         except Exception as e:
#             status = 'unsuccessful'
#             response = str(e)
#
#         # Создаем попытку отправки рассылки
#         MailingAttempt.objects.create(
#             mailing=mailing,
#             recipient=recipient,
#             status=status,
#             response=response
#         )


class RunSendingView(View):
    def post(self, request, sending_id):
        return self.run_sending(sending_id)

    def run_sending(self, sending_id):
        try:
            # Получаем рассылку по ID
            sending = get_object_or_404(Sending, id=sending_id)

            # Проверяем, активна ли рассылка
            if not sending.is_active:
                print("Рассылка неактивна.")
                return

            if sending.start_sending is None:
                sending.start_sending = timezone.now()
            sending.status = 'launched'
            sending.save()

            # Проходим по всем получателям
            for recipient in sending.recipient.all():
                try:
                    # Отправляем сообщение
                    send_mail(
                        subject=sending.message.subject,
                        message=sending.message.message_body,
                        from_email='From-garden@yandex.ru',
                        recipient_list=[recipient.email],
                    )
                    # Логируем успешную попытку
                    MailingAttempt.objects.create(
                        status_attempt='successfully',
                        owner=sending.owner,
                        sending=sending,
                    )
                    print(f"Сообщение успешно отправлено на {recipient.email}")

                except Exception as e:
                    # Логируем неуспешную попытку
                    MailingAttempt.objects.create(
                        status_attempt='unsuccessful',
                        answer=str(e),
                        owner=sending.owner,
                        sending=sending,
                    )
                    print(f"Ошибка при отправке на {recipient.email}: {str(e)}")

            sending.status = 'completed'
            sending.end_sending = timezone.now()
            sending.save()

        except Sending.DoesNotExist:
            print("Рассылка не найдена.")

        return HttpResponseRedirect(reverse('mailing:sending_list'))  # Перенаправление после завершения
