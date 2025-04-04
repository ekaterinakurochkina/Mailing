from django.utils import timezone

from django.db import models
from users.models import User


class MailingRecipient(models.Model):  # Получатель рассылки
    email = models.EmailField(unique=True, verbose_name='Email')  # Email
    name = models.CharField(max_length=150, verbose_name='ФИО', blank=True)  # ФИО
    comment = models.TextField(verbose_name='Комментарий', blank=True)  # комментарий
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Владелец")

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'Получатель рассылки'
        verbose_name_plural = 'Получатели рассылки'
        ordering = ['email']


class Message(models.Model):  # Сообщение
    # sending = models.ForeignKey(Sending, related_name="subject", on_delete=models.SET_NULL, null=True, blank=True,
    #                             verbose_name="Тема сообщения")
    id = models.AutoField(primary_key=True)
    subject = models.CharField(max_length=300, verbose_name='Тема письма')
    message_body = models.TextField(verbose_name='Тело письма', blank=True)  # тело письма
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Владелец")

    def __str__(self):
        return self.subject

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        ordering = ['subject']


class Sending(models.Model):  # Рассылка
    name = models.CharField(max_length=100, verbose_name='Название рассылки')
    start_sending = models.DateTimeField(verbose_name='Дата и время начала рассылки',
                                         default=timezone.now)  # Дата и время первой отправки
    end_sending = models.DateTimeField(verbose_name='Дата и время окончания рассылки', null=True,
                                       blank=True)  # Дата и время окончания отправки
    STATUS_CHOICES = [
        ('created', 'Создана'),
        ('launched', 'Запущена'),
        ('completed', 'Завершена'),
        ('canceled', 'Отменена'),
    ]
    status = models.CharField(max_length=10, verbose_name='Статус', choices=STATUS_CHOICES, default='created')  # статус
    message = models.ForeignKey(Message, related_name="sending", on_delete=models.SET_NULL, null=True, blank=True,
                                verbose_name="Сообщение")  # Сообщение
    recipient = models.ManyToManyField(MailingRecipient,
                                       verbose_name='Укажите получателей рассылки')  # Получатели (связь с моделью Получатель)
    is_active = models.BooleanField(default=True, verbose_name='Действительный')
    owner = models.ForeignKey(User, verbose_name='Владелец', help_text='Владелец рассылки', blank=True, null=True,
                              on_delete=models.SET_NULL)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'
        ordering = ['status']
        permissions = [
            ('can_canceled_sending', 'Может блокировать рассылку ')
        ]


class MailingAttempt(models.Model):  # Попытка рассылки
    date_attempt = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время попытки рассылки')  # Дата и время попытки
    STATUS_CHOICES = [
        ('successfully', 'Успешно'),
        ('unsuccessful', 'Неуспешно'),
    ]
    status_attempt = models.CharField(max_length=15, choices=STATUS_CHOICES, verbose_name='Статус полытки')  # Статус: успешно/неуспешно
    answer = models.TextField(blank=True, null=True, verbose_name='Ответ почтового сервера')  # ответ почтового сервера
    sending = models.ForeignKey(Sending, on_delete=models.PROTECT)  # рассылка (внешн.ключ на модель Рассылка)
    # owner = models.ForeignKey(User, null=True, on_delete=models.CASCADE) # Связь с пользователем
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.status_attempt} - {self.sending.id} - {self.created_at}"

    class Meta:
        verbose_name = 'Попытка рассылки'
        verbose_name_plural = 'Попытки рассылки'
        ordering = ['status_attempt']
