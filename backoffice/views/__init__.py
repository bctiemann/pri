from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import BasicAuthentication, SessionAuthentication

from django.urls import reverse_lazy
from django.utils.dateparse import parse_datetime
from django.views.generic import TemplateView
from django.contrib.auth.views import LogoutView

from users.views import LoginView
from users.models import User


# Home and login/logout views

class AdminViewMixin:

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['admin_users'] = User.objects.filter(is_admin=True)
        return context


class LandingView(AdminViewMixin, TemplateView):
    template_name = 'backoffice/landing.html'


class HomeView(AdminViewMixin, TemplateView):
    template_name = 'backoffice/home.html'


class LoginView(LoginView):
    template_name = 'backoffice/login.html'
    home_url = reverse_lazy('backoffice:home')


class LogoutView(LogoutView):
    pass


# API view to track admin activity

class TrackActivityView(APIView):
    authentication_classes = (BasicAuthentication, SessionAuthentication)

    def post(self, request):
        request.user.admin_last_activity = parse_datetime(request.POST.get('last_activity'))
        request.user.save()
        return Response({
            'is_sleeping': request.user.is_sleeping,
        })
