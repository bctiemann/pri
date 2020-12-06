from django.conf import settings
from django.shortcuts import render, reverse
from django.urls import reverse_lazy
from django.contrib.auth import (
    login, authenticate, get_user_model, password_validation, update_session_auth_hash,
)
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView, LogoutView, INTERNAL_RESET_SESSION_TOKEN
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import DetailView, TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import HttpResponse, JsonResponse, Http404, HttpResponseForbidden, HttpResponseRedirect, HttpResponseNotFound

from two_factor.views import LoginView, PhoneSetupView, PhoneDeleteView, DisableView
from two_factor.forms import AuthenticationTokenForm, BackupTokenForm

from users.forms import UserLoginForm, PasswordChangeForm
from users.models import User

import logging
logger = logging.getLogger(__name__)
auth_logger = logging.getLogger('auth')


class LoginView(LoginView):

    home_url = reverse_lazy('home')
    template_name = 'login.html'
    form_list = (
        ('auth', UserLoginForm),
        ('token', AuthenticationTokenForm),
        ('backup', BackupTokenForm),
    )

    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, request, *args, **kwargs):
        logger.info(f'{request.resolver_match.app_name} login: {request.user} {request.method} '
                    f'{request.POST.get("auth-username")} {request.META.get("REMOTE_ADDR")} '
                    f'{request.POST.get("csrfmiddlewaretoken")}')
        if settings.LOG_AUTH:
            auth_logger.info(f'{request.user} {request.POST}')
        if self.request.user.is_authenticated:
            return HttpResponseRedirect(self.home_url)
        return super(LoginView, self).dispatch(request, *args, **kwargs)


class LogoutView(LogoutView):

    def dispatch(self, request, *args, **kwargs):
        logger.info(f'{request.user} logged out.')
        return super().dispatch(request, *args, **kwargs)


class PasswordChangeView(UpdateView):
    model = User
    form_class = PasswordChangeForm
    template_name = 'accounts/change_password.html'

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        response = super().form_valid(form)
        update_session_auth_hash(self.request, self.request.user)
        return response

    def get_success_url(self):
        return reverse_lazy('change-password-done')


class PasswordChangeDoneView(TemplateView):
    template_name = 'accounts/change_password_done.html'


class PasswordResetView(PasswordResetView):

    def form_valid(self, form):
        logger.info(f'{form.cleaned_data["email"]} requested a password reset')
        return super().form_valid(form)


class PasswordResetConfirmView(PasswordResetConfirmView):
    post_reset_login = True

    def form_valid(self, form):
        logger.info(f'{self.user} successfully reset their password')
        return super().form_valid(form)
