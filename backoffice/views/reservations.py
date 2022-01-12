from rest_framework.views import APIView
from rest_framework.response import Response

from django.shortcuts import render, reverse
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import Http404, HttpResponseRedirect
from django.contrib.auth.mixins import PermissionRequiredMixin

from . import ListViewMixin
from fleet.models import VehicleMarketing
from sales.models import Reservation, Rental
from sales.calculators import RentalPriceCalculator
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
        context['price_data'] = self.object.get_price_data()
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


class ReservationConvertToRentalView(UpdateView):
    model = Reservation
    fields = ()

    def form_valid(self, form):
        reservation = form.instance

        # Populate a new Rental object with fields explicitly from the Reservation
        rental = Rental.objects.create(
            type=Rental.ReservationType.RENTAL,
            vehicle=reservation.vehicle,
            customer=reservation.customer,
            reserved_at=reservation.reserved_at,
            out_at=reservation.out_at,
            back_at=reservation.back_at,
            rate=reservation.rate,
            drivers=reservation.drivers,
            miles_included=reservation.miles_included,
            extra_miles=reservation.extra_miles,
            customer_notes=reservation.customer_notes,
            coupon_code=reservation.coupon_code,
            is_military=reservation.is_military,
            deposit_amount=reservation.deposit_amount,
            confirmation_code=reservation.confirmation_code,
            app_channel=reservation.app_channel,
            delivery_required=reservation.delivery_required,
            tax_percent=reservation.tax_percent,
            delivery_zip=reservation.delivery_zip,
            override_subtotal=reservation.override_subtotal,
            final_price_data=reservation.final_price_data,
            status=Rental.Status.CONFIRMED,
        )
        self.rental = rental

        # We delete the reservation object after converting it to a rental (no harm in this as Rental is a superset
        # of Reservation, except for the status field)
        reservation.delete()

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('backoffice:rental-detail', kwargs={'pk': self.rental.id})
