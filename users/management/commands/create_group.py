from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from users.models import User

# Создание или получение группы
group, created = Group.objects.get_or_create(name="Менеджер")

# Определение прав в группe
permissions = [
    "can_inactivate",
    "can_canceled_sending",
]

# Добавление прав в группу
for perm in permissions:
    # Получаем разрешение
    permission = Permission.objects.get(codename=perm, content_type=ContentType.objects.get_for_model(User))
    group.permissions.add(permission)


# ________
# from django.contrib.auth.models import Permission, Group
# создаём группу "Менеджер"
# if not Group(name="Менеджер"):
#     manager_group = Group.objects.create(name="Менеджер")
#
#     block_user_perm = Permission.objects.get(codename="can_inactivate")
#     block_sending = Permission.objects.get(codename="can_canceled_sending")
#
#     manager_group.permissions.add(block_user_perm, block_sending)
