from django.utils import timezone


from django.db import models
from users.models import User


class MailingRecipient(models.Model):           # Получатель рассылки
    email = models.EmailField(unique=True, verbose_name='Email')                    # Email
    name = models.CharField(max_length=150, verbose_name='ФИО', blank=True)           # ФИО
    comment = models.TextField(verbose_name='Комментарий', blank=True)               # комментарий

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'Получатель рассылки'
        verbose_name_plural = 'Получатели рассылки'
        ordering = ['email']


class Message(models.Model):          #   Сообщение
    # subject = models.ForeignKey(Sending, related_name="subject", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Тема сообщения")
    # id = models.AutoField(primary_key=True)
    subject = models.CharField(max_length=300, verbose_name='Тема письма')           # тема письма
    message_body = models.TextField(verbose_name='Тело письма', blank=True)           # тело письма

    def __str__(self):
        return self.subject

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        ordering = ['subject']


class Sending(models.Model):           # Рассылка
    name = models.CharField(max_length=100, verbose_name="Название рассылки")
    # id = models.AutoField(primary_key=True)
    start_sending = models.DateTimeField(verbose_name='Дата и время начала рассылки', default=timezone.now)              # Дата и время первой отправки
    end_sending = models.DateTimeField(verbose_name='Дата и время окончания рассылки', null=True, blank=True)               # Дата и время окончания отправки
    STATUS_CHOICES = [
        ('created', 'Создана'),
        ('launched', 'Запущена'),
        ('completed', 'Завершена'),
        ('canceled', 'Отменена'),
    ]
    status = models.CharField(max_length=10,verbose_name='Статус', choices=STATUS_CHOICES, default='created')           # статус
    message = models.ForeignKey(Message, related_name="message", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Сообщение")           # Сообщение
    recipient = models.ManyToManyField(MailingRecipient, verbose_name='Получатели')                      # Получатели (связь с моделью Получатель)
    owner = models.ForeignKey(User, verbose_name='Владелец', help_text='Укажите владельца рассылки', blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'
        ordering = ['status']
        permissions = [
            ('can_canceled_sending', 'Can canceled sending')
        ]



class MailingAttempt(models.Model):           # Попытка рассылки
    date_attempt = models.DateTimeField(auto_now_add=True)              # Дата и время попытки
    STATUS_CHOICES = [
        ('successfully', 'Успешно'),
        ('unsuccessful', 'Неуспешно'),
    ]
    status_attempt = models.CharField(max_length=15, choices=STATUS_CHOICES, default='unsuccessful')      # Статус: успешно/неуспешно
    answer = models.TextField(blank=True, null=True)                                       # ответ почтового сервера
    sending = models.ForeignKey(Sending, on_delete=models.PROTECT)               # рассылка (внешн.ключ на модель Рассылка)

    def __str__(self):
        return self.status_attempt

    class Meta:
        verbose_name = 'Попытка рассылки'
        verbose_name_plural = 'Попытки рассылки'
        ordering = ['status_attempt']
