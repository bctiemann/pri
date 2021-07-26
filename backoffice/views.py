from django.shortcuts import render, reverse
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView, LogoutView, INTERNAL_RESET_SESSION_TOKEN

from fleet.models import Vehicle, VehicleMarketing
from backoffice.forms import VehicleForm, VehicleMarketingForm
from users.views import LoginView


# Home and login/logout views

class HomeView(TemplateView):
    template_name = 'backoffice/home.html'


class LoginView(LoginView):
    template_name = 'backoffice/login.html'
    home_url = reverse_lazy('backoffice:home')


class LogoutView(LogoutView):
    pass


# Template generics-based CRUD views

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
    marketing_form_class = VehicleMarketingForm

    def post(self, request, *args, **kwargs):
        marketing_form = VehicleMarketingForm(request.POST)
        print(marketing_form.data)
        print(marketing_form.is_valid())
        print(marketing_form.cleaned_data)
        result = super().post(request, *args, **kwargs)
        VehicleMarketing.objects.filter(vehicle_id=self.object.id).update(**marketing_form.cleaned_data)
        return result

    def get_marketing_form_class(self):
        return self.marketing_form_class

    def get_marketing_form_kwargs(self):
        kwargs = self.get_form_kwargs()
        kwargs['instance'] = kwargs['instance'].vehicle_marketing
        return kwargs

    def get_marketing_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_marketing_form_class()
        return form_class(**self.get_marketing_form_kwargs())

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['marketing_form'] = self.get_marketing_form()
        return context

    def get_success_url(self):
        return reverse('backoffice:vehicle-detail', kwargs={'pk': self.object.id})


class VehicleCreateView(VehicleViewMixin, CreateView):
    model = Vehicle
    template_name = 'backoffice/vehicle_detail.html'
    form_class = VehicleForm
