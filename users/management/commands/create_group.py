from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from users.models import User


class Command(BaseCommand):
    help = 'Создание группы менеджеров с правами блокировки сообщений и пользователей'

    def handle(self, *args, **options):
        # Создание или получение группы менеджеров
        group, created = Group.objects.get_or_create(name='Менеджер')

        # Определение прав
        permissions = [
            'can_inactivate',
            'can_canceled_sending',
        ]

        # Получаем контентный тип для модели User
        content_type = ContentType.objects.get_for_model(User)

        # Добавление прав в группу
        for perm in permissions:
            try:
                # Получаем разрешение
                permission = Permission.objects.get(codename=perm, content_type=content_type)
                group.permissions.add(permission)
            except Permission.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"Право '{perm}' не найдено для модели {User.__name__}."))

        # Сохранение группы (не обязательно, если вы не изменяли её атрибуты)
        group.save()
        self.stdout.write(self.style.SUCCESS('Группа "Менеджер" успешно создана с правами.'))

# -------------вариант 2
# Создание или получение группы
# group, created = Group.objects.get_or_create(name="Менеджер")
#
# # Определение прав в группe
# permissions = [
#     "can_inactivate",
#     "can_canceled_sending",
# ]
#
# # Добавление прав в группу
# for perm in permissions:
#     # Получаем разрешение
#     permission = Permission.objects.get(codename=perm, content_type=ContentType.objects.get_for_model(User))
#     group.permissions.add(permission)


# ________вариант 1
# from django.contrib.auth.models import Permission, Group
# создаём группу "Менеджер"
# if not Group(name="Менеджер"):
#     manager_group = Group.objects.create(name="Менеджер")
#
#     block_user_perm = Permission.objects.get(codename="can_inactivate")
#     block_sending = Permission.objects.get(codename="can_canceled_sending")
#
#     manager_group.permissions.add(block_user_perm, block_sending)
