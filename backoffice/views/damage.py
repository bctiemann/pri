from rest_framework.views import APIView
from rest_framework.response import Response

from django.shortcuts import render, reverse
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import Http404, HttpResponseRedirect
from django.contrib.auth.mixins import PermissionRequiredMixin

from . import ListViewMixin
from backoffice.forms import DamageForm, VehicleSelectorForm
from service.models import Damage
from fleet.models import Vehicle


# Template generics-based CRUD views

class DamageViewMixin:
    model = Damage
    page_group = 'damage'
    default_sort = '-id'
    unrepaired_only = False
    repaired_only = False
    filter_vehicle = None

    @property
    def is_unfiltered_list_view(self):
        return not self.unrepaired_only and not self.repaired_only and super().is_unfiltered_list_view

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.unrepaired_only:
            queryset = queryset.filter(is_repaired=False)
        elif self.repaired_only:
            queryset = queryset.filter(is_repaired=True)
        self.filter_vehicle = self.get_filter_vehicle()
        if self.filter_vehicle:
            queryset = queryset.filter(vehicle=self.filter_vehicle)
        return queryset

    def get_filter_vehicle(self):
        vehicle_id = self.request.GET.get('vehicle_id')
        if vehicle_id:
            return Vehicle.objects.filter(pk=vehicle_id).first()

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['unrepaired_only'] = self.unrepaired_only
        context['repaired_only'] = self.repaired_only
        context['vehicle_selector_form'] = VehicleSelectorForm(
            data={'select_vehicle': self.filter_vehicle.id if self.filter_vehicle else None}
        )
        return context


class DamageListView(PermissionRequiredMixin, DamageViewMixin, ListViewMixin, ListView):
    # PermissionRequiredMixin allows us to specify permission_required (all must be true) for specific models
    permission_required = ('users.view_damage',)
    template_name = 'backoffice/damage/list.html'
    search_fields = ('title', 'notes',)


class DamageDetailView(DamageViewMixin, ListViewMixin, UpdateView):
    template_name = 'backoffice/damage/detail.html'
    form_class = DamageForm

    # def form_valid(self, form):
    #     tax_rate = form.save(commit=False)
    #     tax_rate.total_rate = form.cleaned_data['total_rate_as_percent'] / 100
    #     tax_rate.save()
    #     return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('backoffice:damage-detail', kwargs={'pk': self.object.id})


class DamageCreateView(DamageViewMixin, ListViewMixin, CreateView):
    template_name = 'backoffice/damage/detail.html'
    form_class = DamageForm

    def get_success_url(self):
        return reverse('backoffice:damage-detail', kwargs={'pk': self.object.id})


class DamageDeleteView(DeleteView):
    model = Damage

    def get_success_url(self):
        return reverse('backoffice:damage-list')
