from http.client import responses

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import View
from django.core.mail import send_mail
from django.contrib.auth.mixins import LoginRequiredMixin
from config.settings import CACHE_ENABLED
from mailing.models import MailingRecipient, Message, Sending, MailingAttempt
from django.core.cache import cache
from django.http import HttpResponseForbidden
from users.models import User


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