from django.shortcuts import render, reverse
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from fleet.models import Vehicle
from backoffice.forms import VehicleForm
from users.views import LoginView


class HomeView(TemplateView):
    template_name = 'backoffice/home.html'


class LoginView(LoginView):
    template_name = 'backoffice/login.html'
    home_url = reverse_lazy('backoffice:home')


class VehicleViewMixin:

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['vehicle_model'] = Vehicle
        if 'vehicle_type' in self.kwargs:
            context['vehicle_list'] = context['vehicle_list'].filter(vehicle_type=self.kwargs['vehicle_type'])
        return context


class VehicleListView(VehicleViewMixin, ListView):
    model = Vehicle
    template_name = 'backoffice/vehicle_list.html'


class VehicleDetailView(VehicleViewMixin, UpdateView):
    model = Vehicle
    template_name = 'backoffice/vehicle_detail.html'
    form_class = VehicleForm

    def get_success_url(self):
        return reverse('backoffice:vehicle-detail', kwargs={'pk': self.object.id})


class VehicleCreateView(VehicleViewMixin, CreateView):
    model = Vehicle
    template_name = 'backoffice/vehicle_detail.html'
    form_class = VehicleForm
