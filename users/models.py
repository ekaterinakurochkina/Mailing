from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True, verbose_name="Email")
    phone = models.CharField(max_length=35, verbose_name="Телефон", blank=True, null=True,
                             help_text="Введите номер телефона")
    avatar = models.ImageField(upload_to="users/avatars", verbose_name="Аватар", blank=True, null=True,
                               help_text='Загрузите свой аватар')
    is_active = models.BooleanField(default=True, verbose_name="Действующий")
    token = models.CharField(max_length=100, verbose_name="Token", blank=True, null=True)
    description = models.CharField(max_length=100, verbose_name="Имя", blank=True, null=True,
                                   help_text="Введите ваше имя")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['email']
        permissions = [
            ('can_inactivate', 'Может блокировать пользователя'),
            ('can_canceled_sending', 'Может блокировать рассылку'),
        ]

    @property
    def is_moderator(self) -> bool:
        return self.groups.filter(name='Менеджер').exists()
