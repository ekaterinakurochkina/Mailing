import secrets

from django.contrib.auth import logout
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from config.settings import EMAIL_HOST_USER
from users.forms import UserRegisterForm, UserUpdateForm
from users.models import User


def logout_view(request):
    logout(request)
    return redirect('mailing:home')


# class UserLogoutView(LogoutView):
#     template_name = 'logout.html'


# ____________________________
# блокировка пользователя
# class InactivateUser(LoginRequiredMixin, View):
#     def post(self, request, user_id):
#         user = get_object_or_404(User, id=user_id)
#
#         if not request.user.has_perm('can_inactivate'):
#             return HttpResponseForbidden('У вас нет прав для блокировки пользователя')
#
#         user.is_active = False
#         user.save()
#
#         return redirect('mailing:user_list')


# ______________________блокировка пользователя
@permission_required("users.can_inactivate")
def block_user(self, pk):
    user = get_object_or_404(User, pk=pk)
    user.is_active = False
    user.save()
    return redirect(reverse("users:user_list"))


# ______________________разблокировка пользователя
@permission_required("users.can_inactivate")
def unblock_user(self, pk):
    user = get_object_or_404(User, pk=pk)
    user.is_active = True
    user.save()
    return redirect(reverse("users:user_list"))


# ______________________


# __________________


class UserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = "user_list.html"
    context_object_name = "users"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получаем всех пользователей и добавляем информацию о принадлежности к группе
        for user in context['users']:
            user.is_manager = user.groups.filter(name="Менеджер").exists()
        return context


# class UserDeleteView(LoginRequiredMixin, DeleteView):
#     model = User
#     template_name = "user_confirm_delete.html"
#     success_url = reverse_lazy("mailing:user_list")


class UserCreateView(CreateView):
    model = User
    form_class = UserRegisterForm
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        user = form.save()
        user.is_active = False
        token = secrets.token_hex(16)  # генерируем токен
        user.token = token
        user.save()
        host = self.request.get_host()  # получаем хост, откуда пришел пользователь
        url = f'http://{host}/users/email-confirm/{token}/'
        try:
            send_mail(
                subject="Подтверждение почты",
                message=f"""Спасибо, что зарегистрировались в нашем сервисе!
                Для подтверждения регистрации перейдите по ссылке {url}""",
                from_email=EMAIL_HOST_USER,
                recipient_list=[user.email]
            )
        except Exception as e:
            print(f'Error sending email: {e}')
        return super().form_valid(form)

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['is_manager'] = self.request.user.groups.filter(name="Менеджер").exists()
    #     return context


def email_verification(request, token):
    user = get_object_or_404(User, token=token)
    user.is_active = True
    user.save()
    return redirect(reverse_lazy("users:login"))


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = "users:user_form.html"
    success_url = reverse_lazy("users:user_edit")

    # def get_object(self, queryset=None):
    #     self.object = super().get_object(queryset)
    #     if not self.request.user.is_superuser:
    #         raise PermissionDenied
    #     return self.object
    def dispatch(self, request, *args, **kwargs):
        # Проверяем, является ли текущий пользователь суперпользователем
        if not request.user.is_superuser:
            raise PermissionDenied("У вас нет прав для редактирования этого пользователя.")
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        # Загружаем объект, но проверка прав уже выполнена в dispatch
        return super().get_object(queryset)


class UserDeleteView(LoginRequiredMixin, DeleteView):
    model = User
    template_name = "user_confirm_delete.html"
    success_url = reverse_lazy("users:user_list")

    def get_object(self, queryset=None):
        self.object = super().get_object(queryset)

        # Проверяем, является ли пользователь суперпользователем
        if self.request.user.is_superuser:
            return self.object  # Суперпользователь может удалять любого

        # Проверяем, является ли пользователь менеджером
        if self.request.user.is_staff:  # Предполагаем, что менеджер имеет is_staff
            if self.object.is_superuser:
                raise PermissionDenied("Менеджер не может удалить суперпользователя.")
            return self.object  # Менеджер может удалять обычного пользователя

        # Если пользователь не суперпользователь или менеджер
        raise PermissionDenied("У вас нет прав для удаления этого пользователя.")
