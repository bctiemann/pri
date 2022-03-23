from rest_framework.views import APIView
from rest_framework.response import Response

from django.shortcuts import render, reverse
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import Http404, HttpResponseRedirect
from django.contrib.auth.mixins import PermissionRequiredMixin

from . import ListViewMixin, AdminViewMixin
from backoffice.forms import ConsignmentPaymentForm
from consignment.models import ConsignmentPayment


# Template generics-based CRUD views

class ConsignmentPaymentViewMixin:
    model = ConsignmentPayment
    page_group = 'consignment_payments'
    default_sort = '-id'


class ConsignmentPaymentListView(PermissionRequiredMixin, AdminViewMixin, ConsignmentPaymentViewMixin, ListViewMixin, ListView):
    # PermissionRequiredMixin allows us to specify permission_required (all must be true) for specific models
    permission_required = ('users.view_consignmentpayment',)
    template_name = 'backoffice/consignment_payment/list.html'
    search_fields = ('consigner__first_name', 'consigner__last_name', 'consigner__user__email',)


class ConsignmentPaymentDetailView(AdminViewMixin, ConsignmentPaymentViewMixin, ListViewMixin, UpdateView):
    template_name = 'backoffice/consignment_payment/detail.html'
    form_class = ConsignmentPaymentForm

    def get_success_url(self):
        return reverse('backoffice:consignmentpayment-detail', kwargs={'pk': self.object.id})


class ConsignmentPaymentCreateView(AdminViewMixin, ConsignmentPaymentViewMixin, ListViewMixin, CreateView):
    template_name = 'backoffice/consignment_payment/detail.html'
    form_class = ConsignmentPaymentForm

    def get_success_url(self):
        return reverse('backoffice:consignmentpayment-detail', kwargs={'pk': self.object.id})


class ConsignmentPaymentDeleteView(DeleteView):
    model = ConsignmentPayment

    def get_success_url(self):
        return reverse('backoffice:consignmentpayment-list')
