from django.shortcuts import render
from django.views.generic import TemplateView, FormView, CreateView
from django.urls import reverse_lazy

from users.views import LoginView


class SidebarMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class HomeView(SidebarMixin, TemplateView):
    template_name = 'consignment/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class LoginView(LoginView):
    template_name = 'consignment/login.html'
    home_url = reverse_lazy('consignment:home')


class CalendarView(SidebarMixin, TemplateView):
    template_name = 'consignment/calendar.html'


class ProceedsView(SidebarMixin, TemplateView):
    template_name = 'consignment/proceeds.html'
