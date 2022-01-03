from rest_framework.views import APIView
from rest_framework.response import Response

from django.shortcuts import render, reverse
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import Http404, HttpResponseRedirect
from django.contrib.auth.mixins import PermissionRequiredMixin

from . import ListViewMixin
from fleet.models import VehicleMarketing
from sales.models import Reservation
from sales.utils import RentalPriceCalculator
from backoffice.forms import ReservationForm


# Template generics-based CRUD views

class ReservationViewMixin:
    model = Reservation
    page_group = 'reservations'
    default_sort = '-id'
    paginate_by = 25


class ReservationListView(PermissionRequiredMixin, ReservationViewMixin, ListViewMixin, ListView):
    # PermissionRequiredMixin allows us to specify permission_required (all must be true) for specific models
    permission_required = ('users.view_reservation',)
    template_name = 'backoffice/reservation/list.html'
    search_fields = ('customer__first_name', 'customer__last_name', 'customer__user__email', 'vehicle__make', 'confirmation_code',)


class ReservationDetailView(ReservationViewMixin, ListViewMixin, UpdateView):
    template_name = 'backoffice/reservation/detail.html'
    form_class = ReservationForm

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        vehicle_marketing = VehicleMarketing.objects.get(vehicle_id=self.object.vehicle.id)
        context['vehicle_marketing'] = vehicle_marketing
        price_calculator = RentalPriceCalculator(
            coupon_code=self.object.coupon_code,
            email=self.object.customer.email,
            tax_zip=self.object.delivery_zip,
            effective_date=self.object.out_date,
            is_military=self.object.is_military,
            vehicle_marketing=vehicle_marketing,
            num_days=self.object.num_days,
            extra_miles=self.object.extra_miles,
            override_subtotal=self.object.override_subtotal,
        )
        context['price_data'] = price_calculator.get_price_data()
        return context

    def get_success_url(self):
        return reverse('backoffice:reservation-detail', kwargs={'pk': self.object.id})


class ReservationCreateView(ReservationViewMixin, ListViewMixin, CreateView):
    template_name = 'backoffice/reservation/detail.html'
    form_class = ReservationForm

    def get_success_url(self):
        return reverse('backoffice:reservation-detail', kwargs={'pk': self.object.id})


class ReservationDeleteView(DeleteView):
    model = Reservation

    def get_success_url(self):
        return reverse('backoffice:reservation-list')
