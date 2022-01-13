from rest_framework.views import APIView
from rest_framework.response import Response

from django.shortcuts import render, reverse
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import Http404, HttpResponseRedirect
from django.contrib.auth.mixins import PermissionRequiredMixin

from . import ListViewMixin
from backoffice.forms import AdHocPaymentForm
from sales.models import AdHocPayment


# Template generics-based CRUD views

class AdHocPaymentViewMixin:
    model = AdHocPayment
    page_group = 'adhoc_payments'
    default_sort = '-id'


class AdHocPaymentListView(PermissionRequiredMixin, AdHocPaymentViewMixin, ListViewMixin, ListView):
    # PermissionRequiredMixin allows us to specify permission_required (all must be true) for specific models
    permission_required = ('users.view_adhocpayment',)
    template_name = 'backoffice/adhoc_payment/list.html'
    search_fields = ('item', 'full_name', 'phone',)


class AdHocPaymentDetailView(AdHocPaymentViewMixin, ListViewMixin, UpdateView):
    template_name = 'backoffice/adhoc_payment/detail.html'
    form_class = AdHocPaymentForm

    def get_success_url(self):
        return reverse('backoffice:adhocpayment-detail', kwargs={'pk': self.object.id})


class AdHocPaymentCreateView(AdHocPaymentViewMixin, ListViewMixin, CreateView):
    template_name = 'backoffice/adhoc_payment/detail.html'
    form_class = AdHocPaymentForm

    def get_success_url(self):
        return reverse('backoffice:adhocpayment-detail', kwargs={'pk': self.object.id})


class AdHocPaymentDeleteView(DeleteView):
    model = AdHocPayment

    def get_success_url(self):
        return reverse('backoffice:adhocpayment-list')
