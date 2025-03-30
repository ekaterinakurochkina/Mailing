from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from config.settings import CACHE_ENABLED
from mailing.models import MailingRecipient, Message, Sending, MailingAttempt
from django.core.cache import cache
from django.http import HttpResponseForbidden
from users.models import User

from config.settings import CACHE_ENABLED, EMAIL_HOST_USER
from mailing.models import Sending, MailingAttempt
from users.models import User
from django.http import HttpResponseRedirect

from django.shortcuts import get_object_or_404, redirect
from django.core.mail import send_mail
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

def run_sending(request, pk):
    """Функция запуска рассылки по требованию"""
    sending = get_object_or_404(Sending, id=pk)

    # Установите статус на "запущено" перед началом отправки
    sending.status = "launched"
    sending.save()

    for recipient in MailingRecipient.all():
        try:
            send_mail(
                subject=sending.message.subject,
                message=sending.message.message_body,
                from_email=EMAIL_HOST_USER,
                recipient_list=[recipient.email],
                fail_silently=False,
            )
            MailingAttempt.objects.create(
                date_attempt=timezone.now(),
                status=MailingAttempt.successfully,
                server_response="Email отправлен",
                sending=sending,
            )
        except Exception as e:
            logger.error(f"Ошибка при отправке письма для {recipient.email}: {str(e)}")
            MailingAttempt.objects.create(
                date_attempt=timezone.now(),
                status=MailingAttempt.unsuccessful,
                server_response=str(e),
                sending=sending,
            )

    # Проверяем, нужно ли обновить статус на "завершено"
    if sending.end_sending and sending.end_sending <= timezone.now():
        sending.status = Sending.completed

    sending.save()
    return redirect("mailing:sending_list")


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
        return Sending.objects.all() # проверяем, используется ли кеширование в проекте
    key = "sending_list"        # задаем ключ
    sendings = cache.get(key)   # обращаемся в кеш по этому ключу
    if sendings is not None:
        return sendings         # если кеш пуст
    sendings = Sending.objects.all()    # забираем список рассылок из БД
    cache.set(key, sendings)    # записываем этот список в кеш
    return sendings             # и выдаем пользователю

# def send_mailing(mailing):
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

class InactivateSending(LoginRequiredMixin, View):
    def post(self,request, sending_id):
        sending = get_object_or_404(Sending, id=sending_id)

        if not request.user.has_perm('can_canceled_sending'):
            return HttpResponseForbidden('У вас нет прав для блокировки рассылки')

        sending.status = 'canceled'
        sending.save()

        return redirect('mailing:sending_list')


class InactivateUser(LoginRequiredMixin, View):
    def post(self, request, user_id):
        user = get_object_or_404(User, id=user_id)

        if not request.user.has_perm('can_inactivate'):
            return HttpResponseForbidden('У вас нет прав для блокировки рассылки')

        user.is_active = False
        user.save()

        return redirect('mailing:sending_list')

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