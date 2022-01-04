from rest_framework.views import APIView
from rest_framework.response import Response

from django.shortcuts import render, reverse
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import Http404, HttpResponseRedirect
from django.contrib.auth.mixins import PermissionRequiredMixin

from . import ListViewMixin
from fleet.models import VehicleMarketing
from sales.models import Rental, Driver
from users.models import Customer
from sales.utils import RentalPriceCalculator
from backoffice.forms import RentalForm


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
