from rest_framework.views import APIView
from rest_framework.response import Response

from django.shortcuts import render, reverse
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import Http404, HttpResponseRedirect
from django.contrib.auth.mixins import PermissionRequiredMixin

from . import ListViewMixin
from backoffice.forms import StripeChargeForm, CardForm
from sales.models import Charge


# Template generics-based CRUD views

class StripeChargeViewMixin:
    model = Charge
    page_group = 'stripe_charges'
    default_sort = '-id'


class StripeChargeListView(PermissionRequiredMixin, StripeChargeViewMixin, ListViewMixin, ListView):
    # PermissionRequiredMixin allows us to specify permission_required (all must be true) for specific models
    permission_required = ('users.view_charge',)
    template_name = 'backoffice/stripe_charge/list.html'
    search_fields = ('full_name', 'email', 'phone',)


class StripeChargeDetailView(StripeChargeViewMixin, ListViewMixin, UpdateView):
    template_name = 'backoffice/stripe_charge/detail.html'
    form_class = StripeChargeForm

    def get_success_url(self):
        return reverse('backoffice:charge-detail', kwargs={'pk': self.object.id})


class StripeChargeCreateView(StripeChargeViewMixin, ListViewMixin, CreateView):
    template_name = 'backoffice/stripe_charge/detail.html'
    form_class = StripeChargeForm

    def get_success_url(self):
        return reverse('backoffice:charge-detail', kwargs={'pk': self.object.id})


class StripeChargeChargeView(StripeChargeViewMixin, CreateView):
    template_name = 'backoffice/stripe_charge/charge.html'
    form_class = StripeChargeForm

    def form_invalid(self, form):
        print(form.data)
        print(form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        print(form.data)
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['is_charge_view'] = True
        return context

    def get_success_url(self):
        return reverse('backoffice:charge-list')


class StripeChargeDeleteView(DeleteView):
    model = Charge

    def get_success_url(self):
        return reverse('backoffice:charge-list')
