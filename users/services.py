from email.headerregistry import Group

from django.contrib.auth.decorators import permission_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from mailing.models import Sending
from users.models import User


def email_verification(request, token):
    user = get_object_or_404(User, token=token)
    user.is_active = True
    user.save()
    return HttpResponseRedirect(reverse("users:login"))


@permission_required("users.can_inactivate")
def block_user(self, pk):
    user = User.objects.get(pk=pk)
    user.is_active = {user.is_active: False, not user.is_active: True}[True]
    user.save()
    return redirect(reverse("users:user_list"))



# @permission_required("users.can_canceled_sending")
# def block_sending(self, pk):
#     sending = Sending.objects.get(pk=pk)
#     sending.is_active = {sending.is_active: False, not sending.is_active: True}[True]
#     sending.save()
#     return redirect(reverse("mailing:sending_list"))