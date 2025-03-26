from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone

from config.settings import CACHE_ENABLED, EMAIL_HOST_USER
from mailing.models import Sending, MailingAttempt


def run_sending(request, pk):
    """Функция запуска рассылки по требованию"""
    sending = get_object_or_404(Sending, id=pk)
    for recipient in sending.recipients.all():
        try:
            sending.status = Sending.launched
            send_mail(
                subject=sending.message.subject,
                message=sending.message.content,
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
            print(f"Ошибка при отправке письма для {recipient.email}: {str(e)}")
            MailingAttempt.objects.create(
                date_attempt=timezone.now(),
                status=MailingAttempt.unsuccessful,
                server_response=str(e),
                sending=sending,
            )
    if sending.end_sending and sending.end_sending <= timezone.now():
        # Если время рассылки закончилось, обновляем статус на "завершено"
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


@login_required
def block_mailing(request, pk):
    sending = Sending.objects.get(pk=pk)
    sending.is_active = {sending.is_active: False, not sending.is_active: True}[True]
    sending.save()
    return redirect(reverse("mailing:sending_list"))