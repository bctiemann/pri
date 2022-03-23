from rest_framework.views import APIView
from rest_framework.response import Response

from django.shortcuts import render, reverse
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import Http404, HttpResponseRedirect
from django.contrib.auth.mixins import PermissionRequiredMixin

from . import ListViewMixin, AdminViewMixin
from backoffice.forms import TaxRateForm
from sales.models import TaxRate


# Template generics-based CRUD views

class TaxRateViewMixin:
    model = TaxRate
    page_group = 'tax_rates'
    default_sort = 'postal_code'


class TaxRateListView(PermissionRequiredMixin, AdminViewMixin, TaxRateViewMixin, ListViewMixin, ListView):
    # PermissionRequiredMixin allows us to specify permission_required (all must be true) for specific models
    permission_required = ('users.view_taxrate',)
    template_name = 'backoffice/tax_rate/list.html'
    search_fields = ('postal_code',)


class TaxRateDetailView(AdminViewMixin, TaxRateViewMixin, ListViewMixin, UpdateView):
    template_name = 'backoffice/tax_rate/detail.html'
    form_class = TaxRateForm

    def form_valid(self, form):
        tax_rate = form.save(commit=False)
        tax_rate.total_rate = form.cleaned_data['total_rate_as_percent'] / 100
        tax_rate.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('backoffice:taxrate-detail', kwargs={'pk': self.object.id})


class TaxRateCreateView(AdminViewMixin, TaxRateViewMixin, ListViewMixin, CreateView):
    template_name = 'backoffice/tax_rate/detail.html'
    form_class = TaxRateForm

    def get_success_url(self):
        return reverse('backoffice:taxrate-detail', kwargs={'pk': self.object.id})


class TaxRateDeleteView(DeleteView):
    model = TaxRate

    def get_success_url(self):
        return reverse('backoffice:taxrate-list')
