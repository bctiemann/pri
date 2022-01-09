import logging

from rest_framework.views import APIView
from rest_framework.response import Response

from django_pdfkit import PDFView

from django.conf import settings
from django.shortcuts import render, reverse
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import Http404, HttpResponseRedirect, HttpResponseNotFound
from django.contrib.auth.mixins import PermissionRequiredMixin

from . import ListViewMixin
from fleet.models import VehicleMarketing, VehicleType
from sales.models import Rental, Driver
from users.models import Customer
from sales.utils import RentalPriceCalculator
from backoffice.forms import RentalForm, CloneCustomerForm

logger = logging.getLogger(__name__)


# Template generics-based CRUD views

class RentalViewMixin:
    model = Rental
    page_group = 'rentals'
    default_sort = '-id'
    paginate_by = 25


class RentalListView(PermissionRequiredMixin, RentalViewMixin, ListViewMixin, ListView):
    # PermissionRequiredMixin allows us to specify permission_required (all must be true) for specific models
    permission_required = ('users.view_rental',)
    template_name = 'backoffice/rental/list.html'
    search_fields = ('customer__first_name', 'customer__last_name', 'customer__user__email', 'vehicle__make', 'confirmation_code',)


class RentalDetailView(PermissionRequiredMixin, RentalViewMixin, ListViewMixin, UpdateView):
    permission_required = ('users.edit_rental',)
    template_name = 'backoffice/rental/detail.html'
    form_class = RentalForm

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['price_data'] = self.object.get_price_data()
        context['clone_form'] = CloneCustomerForm(instance=self.object.customer)
        return context

    def get_success_url(self):
        return reverse('backoffice:rental-detail', kwargs={'pk': self.object.id})


class RentalCreateView(PermissionRequiredMixin, RentalViewMixin, ListViewMixin, CreateView):
    template_name = 'backoffice/rental/detail.html'
    permission_required = ('users.create_rental',)
    form_class = RentalForm

    def get_success_url(self):
        return reverse('backoffice:rental-detail', kwargs={'pk': self.object.id})


class RentalDeleteView(PermissionRequiredMixin, RentalViewMixin, DeleteView):
    permission_required = ('users.delete_rental',)

    def get_success_url(self):
        return reverse('backoffice:rental-list')


class RentalDriversView(PermissionRequiredMixin, RentalViewMixin, DetailView):
    template_name = 'backoffice/ajax/drivers.html'
    permission_required = ('users.view_rental',)


class RentalDriverAddView(PermissionRequiredMixin, RentalViewMixin, APIView):
    permission_required = ('users.edit_rental',)

    def post(self, request, pk=None):
        try:
            rental = Rental.objects.get(pk=pk)
        except Rental.DoesNotExist:
            raise Http404
        customer_id = request.POST.get('customer_id')
        try:
            customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            raise Http404

        driver, _ = Driver.objects.get_or_create(rental=rental, customer=customer)

        return Response({'success': True, 'driver_id': driver.id})


class RentalDriverRemoveView(PermissionRequiredMixin, RentalViewMixin, APIView):
    permission_required = ('users.edit_rental',)

    def post(self, request, pk=None):
        try:
            rental = Rental.objects.get(pk=pk)
        except Rental.DoesNotExist:
            raise Http404
        driver_id = request.POST.get('driver_id')
        try:
            driver = Driver.objects.get(pk=driver_id, rental=rental)
        except Driver.DoesNotExist:
            raise Http404

        driver.delete()

        return Response({'success': True})


class RentalDriverPromoteView(PermissionRequiredMixin, RentalViewMixin, APIView):
    permission_required = ('users.edit_rental',)

    def post(self, request, pk=None):
        try:
            rental = Rental.objects.get(pk=pk)
        except Rental.DoesNotExist:
            raise Http404
        driver_id = request.POST.get('driver_id')
        try:
            driver = Driver.objects.get(pk=driver_id, rental=rental)
        except Driver.DoesNotExist:
            raise Http404

        Driver.objects.filter(rental=rental).update(is_primary=False)
        driver.is_primary = True
        driver.save()

        return Response({'success': True})


class RentalGenerateContractView(PermissionRequiredMixin, PDFView):
    permission_required = ('users.view_rental',)
    template_name = 'backoffice/pdf/contract.html'

    def dispatch(self, request, *args, **kwargs):
        try:
            self.rental = Rental.objects.get(pk=self.kwargs['pk'])
        except Rental.DoesNotExist:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_pdfkit_options(self):
        options = {
            'quiet': '',
            'page-size': 'Letter',
            'margin-top': '0.75in',
            'margin-right': '1.0in',
            'margin-bottom': '0.0in',
            'margin-left': '1.0in',
            'encoding': "UTF-8",
            'no-outline': None,
        }
        return options

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rental'] = self.rental
        context['site_url'] = settings.SERVER_BASE_URL
        context['company_name'] = settings.COMPANY_NAME
        context['company_phone'] = settings.COMPANY_PHONE
        context['vehicle_type'] = VehicleType
        return context
