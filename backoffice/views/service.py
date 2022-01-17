from rest_framework.views import APIView
from rest_framework.response import Response

from django.shortcuts import render, reverse
from django.views.generic.list import ListView
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import Http404, HttpResponseRedirect
from django.contrib.auth.mixins import PermissionRequiredMixin

from . import ListViewMixin
from backoffice.forms import ScheduledServiceForm, IncidentalServiceForm, VehicleSelectorForm
from service.models import ScheduledService, IncidentalService
from fleet.models import Vehicle


# Template generics-based CRUD views

class ServiceViewMixin:
    model = ScheduledService
    page_group = 'service'
    default_sort = '-id'
    due_only = False
    upcoming_only = False
    history_only = False
    filter_vehicle = None

    @property
    def is_unfiltered_list_view(self):
        return not self.due_only and not self.upcoming_only and self.history_only and super().is_unfiltered_list_view

    # def get_queryset(self):
    #     queryset = super().get_queryset()
    #     # if self.unrepaired_only:
    #     #     queryset = queryset.filter(is_repaired=False)
    #     # elif self.repaired_only:
    #     #     queryset = queryset.filter(is_repaired=True)
    #     self.filter_vehicle = self.get_filter_vehicle()
    #     if self.filter_vehicle:
    #         queryset = queryset.filter(vehicle=self.filter_vehicle)
    #     return queryset

    def get_filter_vehicle(self):
        vehicle_id = self.request.GET.get('vehicle_id')
        if vehicle_id:
            return Vehicle.objects.filter(pk=vehicle_id).first()

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['due_only'] = self.due_only
        context['upcoming_only'] = self.upcoming_only
        context['history_only'] = self.history_only
        filter_vehicle = self.get_filter_vehicle()
        context['vehicle_selector_form'] = VehicleSelectorForm(
            data={'select_vehicle': filter_vehicle.id if filter_vehicle else None}
        )
        context['filter_vehicle'] = filter_vehicle
        return context


class DueServiceListView(PermissionRequiredMixin, ServiceViewMixin, ListViewMixin, ListView):
    # PermissionRequiredMixin allows us to specify permission_required (all must be true) for specific models
    permission_required = ('users.view_service',)
    template_name = 'backoffice/service/list_due.html'
    search_fields = ('title', 'notes',)
    model = Vehicle


class UpcomingServiceListView(PermissionRequiredMixin, ServiceViewMixin, ListViewMixin, ListView):
    # PermissionRequiredMixin allows us to specify permission_required (all must be true) for specific models
    permission_required = ('users.view_service',)
    template_name = 'backoffice/service/list_upcoming.html'
    search_fields = ('title', 'notes',)
    model = Vehicle


class ServiceHistoryListView(PermissionRequiredMixin, ServiceViewMixin, ListViewMixin, TemplateView):
    # PermissionRequiredMixin allows us to specify permission_required (all must be true) for specific models
    permission_required = ('users.view_service',)
    template_name = 'backoffice/service/list_history.html'
    search_fields = ('title', 'notes',)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['incidental_services'] = IncidentalService.objects.filter(vehicle=context['filter_vehicle'])
        context['scheduled_services'] = ScheduledService.objects.filter(vehicle=context['filter_vehicle'])
        return context


class ScheduledServiceDetailView(ServiceViewMixin, ListViewMixin, UpdateView):
    template_name = 'backoffice/service/detail_scheduled.html'
    form_class = ScheduledServiceForm

    # def form_valid(self, form):
    #     tax_rate = form.save(commit=False)
    #     tax_rate.total_rate = form.cleaned_data['total_rate_as_percent'] / 100
    #     tax_rate.save()
    #     return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('backoffice:service-detail-scheduled', kwargs={'pk': self.object.id})


class ScheduledServiceCreateView(ServiceViewMixin, ListViewMixin, CreateView):
    template_name = 'backoffice/service/detail_scheduled.html'
    form_class = ScheduledServiceForm

    def get_success_url(self):
        return reverse('backoffice:service-detail-scheduled', kwargs={'pk': self.object.id})


class IncidentalServiceDetailView(ServiceViewMixin, ListViewMixin, UpdateView):
    template_name = 'backoffice/service/detail_incidental.html'
    form_class = IncidentalServiceForm
    model = IncidentalService

    # def form_valid(self, form):
    #     tax_rate = form.save(commit=False)
    #     tax_rate.total_rate = form.cleaned_data['total_rate_as_percent'] / 100
    #     tax_rate.save()
    #     return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('backoffice:service-detail-incidental', kwargs={'pk': self.object.id})


class IncidentalServiceCreateView(ServiceViewMixin, ListViewMixin, CreateView):
    template_name = 'backoffice/service/detail_incidental.html'
    form_class = IncidentalServiceForm
    model = IncidentalService

    def get_success_url(self):
        return reverse('backoffice:service-detail-incidental', kwargs={'pk': self.object.id})


class ScheduledServiceDeleteView(DeleteView):
    model = ScheduledService

    def get_success_url(self):
        return reverse('backoffice:service-list-due')


class IncidentalServiceDeleteView(DeleteView):
    model = IncidentalService

    def get_success_url(self):
        return reverse('backoffice:service-list-history')
