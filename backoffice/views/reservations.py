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
from users.models import Customer, User, generate_password
from sales.models import Reservation, Rental, Driver
from sales.calculators import RentalPriceCalculator
from backoffice.forms import ReservationForm, ReservationCreateForm, RentalConversionForm


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
    form_class = ReservationCreateForm

    def form_valid(self, form):
        reservation = form.save()
        self.object = reservation

        customer = form.cleaned_data['customer']
        if customer:
            if form.cleaned_data['send_email']:
                reservation.send_welcome_email(
                    email_text_template='email/reservation_confirm_existing_customer.txt',
                    email_html_template='email/reservation_confirm_existing_customer.html',
                )
        else:
            user = User.objects.create_user(email=form.cleaned_data['email'], password=generate_password())
            customer = Customer.objects.create(
                user=user,
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                mobile_phone=form.cleaned_data['mobile_phone'],
                work_phone=form.cleaned_data['work_phone'],
                home_phone=form.cleaned_data['home_phone']
            )
            if form.cleaned_data['send_email']:
                reservation.send_welcome_email()

        reservation.customer = customer
        reservation.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = super().get_form_kwargs()
        customer_id = self.request.GET.get('customer_id')
        if customer_id:
            try:
                kwargs['initial']['customer'] = Customer.objects.get(pk=customer_id)
            except Customer.DoesNotExist:
                pass
        return kwargs

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
        reservation_data['damage_out'] = reservation.vehicle.damage
        rental_form = RentalConversionForm(data=reservation_data)
        self.rental = rental_form.save()

        # Add the customer as the rental's primary driver
        Driver.objects.create(rental=self.rental, customer=self.rental.customer, is_primary=True)

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('backoffice:rental-detail', kwargs={'pk': self.rental.id})
