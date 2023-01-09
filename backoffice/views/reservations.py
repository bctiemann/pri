from rest_framework.views import APIView
from rest_framework.response import Response

from django.shortcuts import render, reverse
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import Http404, HttpResponseRedirect
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.forms.models import model_to_dict

from . import ListViewMixin, AdminViewMixin
from fleet.models import VehicleMarketing
from sales.models import Reservation, Rental, Driver
from sales.calculators import RentalPriceCalculator
from backoffice.forms import ReservationForm, RentalConversionForm


# Template generics-based CRUD views

class ReservationViewMixin:
    model = Reservation
    page_group = 'reservations'
    default_sort = '-id'
    paginate_by = 25


class ReservationListView(PermissionRequiredMixin, AdminViewMixin, ReservationViewMixin, ListViewMixin, ListView):
    # PermissionRequiredMixin allows us to specify permission_required (all must be true) for specific models
    permission_required = ('users.view_reservation',)
    template_name = 'backoffice/reservation/list.html'
    search_fields = ('customer__first_name', 'customer__last_name', 'customer__user__email', 'vehicle__make', 'confirmation_code',)


class ReservationDetailView(AdminViewMixin, ReservationViewMixin, ListViewMixin, UpdateView):
    template_name = 'backoffice/reservation/detail.html'
    form_class = ReservationForm

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['price_data'] = self.object.get_price_data()
        return context

    def get_success_url(self):
        return reverse('backoffice:reservation-detail', kwargs={'pk': self.object.id})


class ReservationCreateView(AdminViewMixin, ReservationViewMixin, ListViewMixin, CreateView):
    template_name = 'backoffice/reservation/detail.html'
    form_class = ReservationForm

    # TODO: if form.send_email, reservation.send_welcome_email()
    #  If existing customer, use reservation_confirm_existing_customer.txt

    def get_success_url(self):
        return reverse('backoffice:reservation-detail', kwargs={'pk': self.object.id})


class ReservationDeleteView(DeleteView):
    model = Reservation

    def get_success_url(self):
        return reverse('backoffice:reservation-list')


class ReservationConvertToRentalView(UpdateView):
    model = Reservation
    fields = ()
    rental = None

    def form_valid(self, form):
        reservation = form.instance

        # Collect all the field values from the BaseReservation, which will be used to create the Rental
        reservation_data = model_to_dict(reservation)

        # We delete the Reservation object before converting it to a Rental (no harm in this as Rental is a superset
        # of Reservation, except for the status field). Have to delete prior to creating rental to avoid collision
        # of confirmation_code.
        reservation.delete()

        reservation_data['status'] = Rental.Status.CONFIRMED
        rental_form = RentalConversionForm(data=reservation_data)
        self.rental = rental_form.save()

        # Add the customer as the rental's primary driver
        Driver.objects.create(rental=self.rental, customer=self.rental.customer, is_primary=True)

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('backoffice:rental-detail', kwargs={'pk': self.rental.id})
