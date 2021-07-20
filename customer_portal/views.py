from django.views.generic import TemplateView, FormView, CreateView
from django.http import Http404
from django.urls import reverse_lazy

from fleet.models import Vehicle, VehicleMarketing, VehicleType, VehicleStatus
from users.views import LoginView


# This mixin allows us to include the common query for cars and bikes into every view, for the nav menu
class NavMenuMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ready_vehicles'] = VehicleMarketing.objects.filter(status=VehicleStatus.READY).order_by('-weighting')
        context['cars'] = context['ready_vehicles'].filter(vehicle_type=VehicleType.CAR)
        context['bikes'] = context['ready_vehicles'].filter(vehicle_type=VehicleType.BIKE)
        return context


class HomeView(TemplateView):
    template_name = 'customer_portal/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class LoginView(LoginView):
    template_name = 'customer_portal/login.html'
    home_url = reverse_lazy('customer_portal:home')
