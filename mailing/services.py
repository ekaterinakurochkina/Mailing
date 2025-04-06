import logging

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import Group
from django.core.cache import cache
from django.core.mail import send_mail
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.views.generic import View

from config.settings import CACHE_ENABLED

logger = logging.getLogger(__name__)

from .models import MailingAttempt, Sending
from django.views import View
from django.http import HttpResponseRedirect
from django.urls import reverse

class RunSendingView(View):
    def get(self, request, sending_id):
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


# def run_sending(sending_id):
#     try:
#         # Получаем рассылку по ID
#         sending = get_object_or_404(Sending, id=sending_id)
#         # sending = Sending.objects.get(id=sending_id)
#
#         # Проверяем, активна ли рассылка
#         if not sending.is_active:
#             print("Рассылка неактивна.")
#             return
#
#         if sending.start_sending is None:
#             sending.start_sending = timezone.now()
#         sending.status ='launched'
#         sending.save()
#
#         # Проходим по всем получателям
#         for recipient in sending.recipient.all():
#             try:
#                 # Отправляем сообщение
#                 send_mail(
#                     subject=sending.message.subject,
#                     message=sending.message.message_body,
#                     from_email='From-garden@yandex.ru',
#                     recipient_list=[recipient.email],
#                 )
#                 # Логируем успешную попытку
#                 MailingAttempt.objects.create(
#                     status_attempt='successfully',
#                     owner=sending.owner,
#                     sending=sending,
#                 )
#                 print(f"Сообщение успешно отправлено на {recipient.email}")
#
#             except Exception as e:
#                 # Логируем неуспешную попытку
#                 MailingAttempt.objects.create(
#                     status_attempt='unsuccessful',
#                     answer=str(e),
#                     owner=sending.owner,
#                     sending=sending,
#                 )
#                 print(f"Ошибка при отправке на {recipient.email}: {str(e)}")
#             finally:
#                 sending.status = 'completed'
#                 sending.end_sending = timezone.now()
#                 sending.save()
#                 # redirect("mailing:sending_list")
#
#     except Sending.DoesNotExist:
#         print("Рассылка не найдена.")


def statistics_view(request):
    user = request.user

    if user.is_superuser:
        attempts = MailingAttempt.objects.all().order_by('-date_attempt')  # Все попытки для суперпользователя
    elif user.groups.filter(name='Менеджер').exists():
        attempts = MailingAttempt.objects.all().order_by('-date_attempt')  # Все попытки для менеджера
    else:
        attempts = MailingAttempt.objects.filter(owner=user).order_by(
            '-date_attempt')  # Только свои рассылки для обычного пользователя

    return render(request, 'statistics.html', {'attempts': attempts})


class BlockSendingView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'mailing.can_canceled_sending'

    def post(self, request, sending_id):
        sending = get_object_or_404(Sending, id=sending_id)
        sending.status = 'canceled'
        sending.save()
        return redirect(reverse("mailing:sending_list"))

class UnblockSendingView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'mailing.can_canceled_sending'

    def post(self, request, sending_id):
        sending = get_object_or_404(Sending, id=sending_id)
        sending.status = 'created'
        sending.save()
        return redirect(reverse("mailing:sending_list"))


# def block_sending(self, pk):
#     sending = Sending.objects.get(pk=pk)
#     sending.is_active = {sending.is_active: False, not sending.is_active: True}[True]
#     sending.save()
#     return redirect(reverse("mailing:sending_list"))
# _____________________
# def run_sending(request, pk):
#     """Функция запуска рассылки по требованию"""
#     sending = get_object_or_404(Sending, id=pk)
#
#     # Установите статус на "запущено" перед началом отправки
#     sending.status = "launched"
#     sending.save()
#
#     for recipient in MailingRecipient():
#         try:
#             send_mail(
#                 subject=sending.message.subject,
#                 message=sending.message.message_body,
#                 from_email=EMAIL_HOST_USER,
#                 recipient_list=[recipient.email],
#                 fail_silently=False,
#             )
#             MailingAttempt.objects.create(
#                 date_attempt=timezone.now(),
#                 status=MailingAttempt.successfully,
#                 server_response="Email отправлен",
#                 sending=sending,
#             )
#         except Exception as e:
#             logger.error(f"Ошибка при отправке письма для {recipient.email}: {str(e)}")
#             MailingAttempt.objects.create(
#                 date_attempt=timezone.now(),
#                 status=MailingAttempt.unsuccessful,
#                 server_response=str(e),
#                 sending=sending,
#             )
#
#     # Проверяем, нужно ли обновить статус на "завершено"
#     if sending.end_sending and sending.end_sending <= timezone.now():
#         sending.status = Sending.completed
#
#     sending.save()
#     return redirect("mailing:sending_list")


def get_mailing_from_cache():
    """Получение данных по рассылкам из кэша, если кэш пуст берем из БД."""
    if not CACHE_ENABLED:
        return Sending.objects.all()
    key = "sending_list"
    cache_data = cache.get(key)
    if cache_data is not None:
        return cache_data
    cache_data = Sending.objects.all()
    cache.set(key, cache_data)
    return cache_data


def get_attempt_from_cache():
    """Получение данных по попыткам из кэша, если кэш пуст берем из БД."""
    if not CACHE_ENABLED:
        return MailingAttempt.objects.all()
    key = "attempt_list"
    cache_data = cache.get(key)
    if cache_data is not None:
        return cache_data
    cache_data = MailingAttempt.objects.all()
    cache.set(key, cache_data)
    return cache_data


def get_object_from_cache():
    """Функция низкоуровневого кеширования для списка рассылок"""
    if not CACHE_ENABLED:
        return Sending.objects.all()  # проверяем, используется ли кеширование в проекте
    key = "sending_list"  # задаем ключ
    sendings = cache.get(key)  # обращаемся в кеш по этому ключу
    if sendings is not None:
        return sendings  # если кеш пуст
    sendings = Sending.objects.all()  # забираем список рассылок из БД
    cache.set(key, sendings)  # записываем этот список в кеш
    return sendings  # и выдаем пользователю


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



# class InactivateUser(LoginRequiredMixin, View):
#     def post(self, request, user_id):
#         user = get_object_or_404(User, id=user_id)
#
#         if not request.user.has_perm('can_inactivate'):
#             return HttpResponseForbidden('У вас нет прав для блокировки рассылки')
#
#         user.is_active = False
#         user.save()
#
#         return redirect('mailing:sending_list')

# def run_mailing(request, pk):
#     """Функция запуска рассылки по требованию"""
#     mailing = get_object_or_404(Sending, id=pk)
#     for recipient in mailing.recipients.all():
#         try:
#             mailing.status = Sending.launched
#             send_mail(
#                 subject=mailing.message.subject,
#                 message=mailing.message.message_body,
#                 from_email=EMAIL_HOST_USER,
#                 recipient_list=[recipient.email],
#                 fail_silently=False,
#             )
#             MailingAttempt.objects.create(
#                 date_attempt=timezone.now(),
#                 status=MailingAttempt.successfully,
#                 server_response="Email отправлен",
#                 mailing=mailing,
#             )
#         except Exception as e:
#             print(f"Ошибка при отправке письма для {recipient.email}: {str(e)}")
#             MailingAttempt.objects.create(
#                 date_attempt=timezone.now(),
#                 status=MailingAttempt.unsuccessful,
#                 server_response=str(e),
#                 mailing=mailing,
#             )
#     if mailing.end_sending and mailing.end_sending <= timezone.now():
#         # Если время рассылки закончилось, обновляем статус на "завершено"
#         mailing.status = Sending.completed
#     mailing.save()
#     return redirect("mailing:sending_list")

# ('created', 'Создана'),
# ('launched', 'Запущена'),
# ('completed', 'Завершена'),
# ('canceled', 'Отменена'),
# ('successfully', 'Успешно'),
# ('unsuccessful', 'Неуспешно'),
