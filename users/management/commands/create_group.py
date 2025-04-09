from django.contrib.auth.models import Permission, Group

# создаём группу "Менеджер"
if not Group(name="Менеджер"):
    manager_group = Group.objects.create(name="Менеджер")

    block_user_perm = Permission.objects.get(codename="can_inactivate")
    block_sending = Permission.objects.get(codename="can_canceled_sending")

    manager_group.permissions.add(block_user_perm, block_sending)
