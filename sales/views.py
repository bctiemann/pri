from django.views.generic import TemplateView, FormView, CreateView, UpdateView
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import reverse
from django.db import IntegrityError
from django.contrib.auth import authenticate, login
from django import forms

from rest_framework.response import Response
from rest_framework.exceptions import APIException

from users.models import User, Customer
from sales.forms import (
    ReservationRentalDetailsForm, ReservationRentalPaymentForm, ReservationRentalLoginForm,
    PerformanceExperienceDetailsForm, PerformanceExperiencePaymentForm, PerformanceExperienceLoginForm,
    JoyRideDetailsForm, JoyRidePaymentForm, JoyRideLoginForm,
    GiftCertificateForm,
)
from sales.models import GiftCertificate, generate_code
from sales.enums import ServiceType
from marketing.views import NavMenuMixin
from fleet.models import Vehicle, VehicleMarketing, VehicleType, VehicleStatus

customer_fields = (
    'first_name', 'last_name', 'mobile_phone', 'home_phone', 'work_phone', 'fax', 'cc_number', 'cc_exp_yr',
    'cc_exp_mo', 'cc_cvv', 'cc_phone', 'address_line_1', 'address_line_2', 'city', 'state', 'zip'
)


# All 2-part forms (where the first phase collects the reservation details, and the second phase is either a login form
# or a payment details/new user creation form depending on the email address given in the first phase) use this mixin.
class PaymentLoginFormMixin:

    def get_payment_form_class(self):
        return self.payment_form_class

    def get_payment_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_payment_form_class()
        return form_class(**self.get_form_kwargs())

    def get_login_form_class(self):
        return self.login_form_class

    def get_login_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_login_form_class()
        return form_class(**self.get_form_kwargs())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['payment_form'] = self.get_payment_form()
        context['login_form'] = self.get_login_form()
        # context['form_type'] = self.form_type
        return context


# Mixin to get the resolved and authenticated customer from the reservation form, creating it new if necessary;
# also to provide a consolidated post() method which creates a reservation of any type attached to the customer.
# ReCAPTCHA is checked in the form's clean() method provided by ReCAPTCHAFormMixin.
class ReservationMixin:

    @staticmethod
    def _get_login_customer(request, form):
        if form.customer:
            # TODO: If authenticated user is not the same as the user in the request, logout and re-auth using POST data
            if request.user.is_authenticated:
                return form.customer
            if authenticate(request, username=form.customer.email, password=form.cleaned_data['password']):
                login(request, form.customer.user)
                return form.customer
            # Only way to return None is if password is incorrect for an existing user's email
            return None
        else:
            # Create Customer object and login
            # TODO: Ensure that every User has a Customer attached, as providing an email of an unattached user will
            #  try to create a new user which will fail the uniqueness constraint. Alternatively, do a get_or_create
            #  user = User.objects.create_user(form.cleaned_data['email'], password=generate_password())
            new_password = form.cleaned_data.get('password_new')
            # User changed email address after submitting a valid one in the details form
            if not new_password:
                return None
            user = User.objects.create_user(form.cleaned_data['email'], password=new_password)
            customer_kwargs = {key: form.cleaned_data.get(key) for key in customer_fields}
            # Create the customer object. Stripe cards are not registered until the Customer has an id (has been saved).
            customer = Customer.objects.create(
                user=user,
                registration_ip=request.remote_ip,
                **customer_kwargs,
            )
            # Save a second time to register Stripe cards
            customer.save()
            login(request, user)
        return customer

    def create_reservation(self, request, form=None):
        form = form or self.form_class(request.POST)
        print(form.data)
        print(form.is_valid())
        print(form.errors.as_json())
        if not form.is_valid():
            return {
                'success': False,
                'errors': form.errors,
            }

        # TODO: kill switch
        kill_switch = False
        if kill_switch:
            return {
                'success': True,
                'reservation_type': self.reservation_type,
                'customer_site_url': self.get_honeypot_url(form=form),
            }

        # Create Customer or login existing user
        customer = self._get_login_customer(request, form)
        if not customer:
            return {
                'success': False,
                'errors': {
                    'password': ['Incorrect password'],
                },
            }

        # TODO: Check IP here. If more than 2 customers created with the same IP in the last 10 minutes, fail silently.
        #  Push to honeypot success page.

        # Create Reservation

        reservation = form.save(commit=False)
        reservation.customer = customer

        # If rental, resolve vehicle
        if 'vehicle_marketing' in form.cleaned_data:
            reservation.vehicle = form.cleaned_data['vehicle_marketing'].vehicle

        try:
            reservation.save()
        except IntegrityError as e:
            raise APIException(detail=e, code='collision')

        return {
            'success': form.is_valid(),
            'errors': form.errors,
            'errors_html': form.errors.as_ul(),
            'reservation_type': self.reservation_type,
            'customer_site_url': self.get_customer_site_url(confirmation_code=reservation.confirmation_code),
        }

    def get_customer_site_url(self, **kwargs):
        raise NotImplementedError

    def get_honeypot_url(self, **kwargs):
        raise NotImplementedError


class NoJSFlowMixin:

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            if form.form_type == 'details':
                if form.customer:
                    form_type = 'login'
                else:
                    form_type = 'payment'
                return self.render_to_response(self.get_context_data(form=form, form_type=form_type, **kwargs))
            return self.form_valid(form)
        else:
            return self.form_invalid(form, **kwargs)

    def form_valid(self, form):
        # return HttpResponseRedirect(self.get_success_url())
        reservation_result = self.create_reservation(self.request, form)
        if reservation_result['success']:
            return HttpResponseRedirect(reservation_result['customer_site_url'])
        for field, error in reservation_result['errors'].items():
            form.add_error(field, forms.ValidationError(error))
        return self.form_invalid(form)

    def form_invalid(self, form, **kwargs):
        context = self.get_context_data(form=form, form_type=form.form_type, **kwargs)
        context['login_form'] = form
        context['payment_form'] = form
        for field in form.errors:
            form[field].field.widget.attrs.setdefault('class', '')
            form[field].field.widget.attrs['class'] += ' field-error'
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        form = kwargs.get('form')
        form_type = kwargs.get('form_type')
        context = super().get_context_data(**kwargs)
        context['form_type'] = form_type or 'details'
        if form:
            context['price_data'] = form.price_data
        return context


class VehicleMixin:

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data(**kwargs))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs.get('slug')
        # We filter() rather than get() because vehicle_marketing.slug is not unique (we may have multiple of the
        # same vehicle)
        context['vehicle'] = VehicleMarketing.objects.filter(slug=slug, status=VehicleStatus.READY).first()
        if not context['vehicle']:
            raise Http404
        return context


# This template is rendered with three forms: details (phase 1), payment (phase 2 for new user), and login (phase 2 for
# returning user. All three forms have different validation needs and field sets
class ReserveView(NavMenuMixin, PaymentLoginFormMixin, ReservationMixin, NoJSFlowMixin, VehicleMixin, FormView):
    template_name = 'front_site/reserve/reserve.html'
    form_class = ReservationRentalDetailsForm
    payment_form_class = ReservationRentalPaymentForm
    login_form_class = ReservationRentalLoginForm
    form_type = 'details1'
    reservation_type = ServiceType.RENTAL

    # def get(self, request, *args, **kwargs):
    #     return self.render_to_response(self.get_context_data(**kwargs))

    # def post(self, request, *args, **kwargs):
    #     """
    #     Handle POST requests: instantiate a form instance with the passed
    #     POST variables and then check if it's valid.
    #     """
    #     form = self.get_form()
    #     if form.is_valid():
    #         if form.form_type == 'details':
    #         # if isinstance(form, ReservationRentalDetailsForm):
    #             # new_form = None
    #             if form.customer:
    #                 form_type = 'login'
    #             #     new_form = ReservationRentalLoginForm(**self.get_form_kwargs())
    #             # #     # return reverse('reserve-login-form', kwargs={'slug': form.vehicle.slug})
    #             else:
    #                 form_type = 'payment'
    #             #     new_form = ReservationRentalPaymentForm(**self.get_form_kwargs())
    #             return self.render_to_response(self.get_context_data(form=form, form_type=form_type, **kwargs))
    #             # # return reverse('reserve-payment-form', kwargs={'slug': form.vehicle.slug})
    #
    #         return self.form_valid(form)
    #     else:
    #         return self.form_invalid(form, **kwargs)

    # def get_form_class(self):
    #     if self.form_type == 'details':
    #         return self.form_class
    #     elif self.form_type =

    # def form_valid(self, form):
    #     success_url = reverse('reserve-honeypot', kwargs={'slug': form.vehicle.slug})
    #     return HttpResponseRedirect(success_url)
    #     # reservation_result = self.create_reservation(self.request, form)
    #     # if reservation_result['success']:
    #     #     return HttpResponseRedirect(reservation_result['customer_site_url'])
    #     # return self.render_to_response(self.get_context_data(form=form, form_type=self.form_type, slug=form.vehicle.slug))

    # def form_invalid(self, form, **kwargs):
    #     """If the form is invalid, render the invalid form."""
    #     for field in form.errors:
    #         form[field].field.widget.attrs.setdefault('class', '')
    #         form[field].field.widget.attrs['class'] += ' field-error'
    #     return self.render_to_response(self.get_context_data(form=form, form_type=form.form_type, **kwargs))

    # def get_payment_form_class(self):
    #     return self.payment_form_class
    #
    # def get_payment_form(self, form_class=None):
    #     if form_class is None:
    #         form_class = self.get_payment_form_class()
    #     return form_class(**self.get_form_kwargs())
    #
    # def get_login_form_class(self):
    #     return self.login_form_class
    #
    # def get_login_form(self, form_class=None):
    #     if form_class is None:
    #         form_class = self.get_login_form_class()
    #     return form_class(**self.get_form_kwargs())

    # def get_context_data(self, slug=None, form=None, form_type=None, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     # We filter() rather than get() because vehicle_marketing.slug is not unique (we may have multiple of the
    #     # same vehicle)
    #     context['vehicle'] = VehicleMarketing.objects.filter(slug=slug, status=VehicleStatus.READY).first()
    #     if not context['vehicle']:
    #         raise Http404
    #     # context['payment_form'] = self.get_payment_form()
    #     # context['login_form'] = self.get_login_form()
    #     context['form_type'] = form_type or 'details'
    #     if form:
    #         context['price_data'] = form.price_data
    #     return context

    # def get_success_url(self):
    #     form = self.get_form()
    #     # form.is_valid()
    #     # vehicle_marketing = form.cleaned_data['vehicle_marketing']
    #     if isinstance(form, ReservationRentalDetailsForm):
    #         if form.customer:
    #             return reverse('reserve-login', kwargs={'slug': form.vehicle.slug})
    #         return reverse('reserve-payment', kwargs={'slug': form.vehicle.slug})
    #     return reverse('reserve', kwargs={'slug': form.vehicle.slug})

    # def get_success_url(self):
    #     return reverse('reserve-honeypot', kwargs={'slug': form.vehicle.slug})

    def get_honeypot_url(self, **kwargs):
        return reverse('reserve-honeypot')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reservation_type'] = ServiceType.RENTAL
        return context

    def get_customer_site_url(self, confirmation_code):
        return reverse('customer_portal:confirm-reservation', kwargs={'confirmation_code': confirmation_code})


class ReserveLoginFormView(ReserveView):
    template_name = 'front_site/reserve/login_form.html'
    form_class = ReservationRentalLoginForm


class ReservePaymentFormView(ReserveView):
    template_name = 'front_site/reserve/payment_form.html'
    form_class = ReservationRentalPaymentForm


class ReservePriceBreakdownView(VehicleMixin, FormView):
    template_name = 'front_site/reserve/price_breakdown.html'
    form_class = ReservationRentalDetailsForm

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.render_to_response(self.get_context_data(form=form, **kwargs))

    def get_context_data(self, **kwargs):
        form = kwargs.get('form')
        context = super().get_context_data(**kwargs)
        # context['vehicle'] = VehicleMarketing.objects.filter(slug=slug, status=VehicleStatus.READY).first()
        # if not context['vehicle']:
        #     raise Http404
        context['price_data'] = form.price_data
        return context


class ReserveHoneypotView(NavMenuMixin, VehicleMixin, TemplateView):
    template_name = 'front_site/reserve/honeypot.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['vehicle'] = VehicleMarketing.objects.filter(slug=slug, status=VehicleStatus.READY).first()
        # if not context['vehicle']:
        #     raise Http404
        context['confirmation_code'] = generate_code(ServiceType.RENTAL)
        return context


# Performance Experience

class PerformanceExperienceView(NavMenuMixin, PaymentLoginFormMixin, FormView):
    template_name = 'front_site/performance_experience/reserve.html'
    form_class = PerformanceExperienceDetailsForm
    payment_form_class = PerformanceExperiencePaymentForm
    login_form_class = PerformanceExperienceLoginForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['vehicle_type'] = VehicleType
        return context


# Joy Ride

class JoyRideView(NavMenuMixin, PaymentLoginFormMixin, ReservationMixin, NoJSFlowMixin, FormView):
    template_name = 'front_site/joy_ride/reserve.html'
    form_class = JoyRideDetailsForm
    payment_form_class = JoyRidePaymentForm
    login_form_class = JoyRideLoginForm
    reservation_type = ServiceType.JOY_RIDE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['vehicle_type'] = VehicleType
        context['reservation_type'] = ServiceType.JOY_RIDE
        return context

    def get_customer_site_url(self, confirmation_code):
        return reverse('customer_portal:joyride-confirm', kwargs={'confirmation_code': confirmation_code})

    def get_honeypot_url(self, **kwargs):
        return reverse('joy-ride-honeypot')


class JoyRideLoginFormView(JoyRideView):
    template_name = 'front_site/includes/login_form.html'
    form_class = JoyRideLoginForm


class JoyRidePaymentFormView(JoyRideView):
    template_name = 'front_site/includes/payment_form.html'
    form_class = JoyRidePaymentForm


class JoyRidePriceBreakdownView(FormView):
    template_name = 'front_site/joy_ride/price_breakdown.html'
    form_class = JoyRideDetailsForm

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.render_to_response(self.get_context_data(form=form, **kwargs))

    def get_context_data(self, slug=None, form=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['price_data'] = form.price_data
        return context


class JoyRideHoneypotView(NavMenuMixin, TemplateView):
    template_name = 'front_site/joy_ride/honeypot.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['confirmation_code'] = generate_code(ServiceType.JOY_RIDE)
        return context


# Gift Certificate

class GiftCertificateView(NavMenuMixin, CreateView):
    template_name = 'front_site/gift_certificate.html'
    form_class = GiftCertificateForm
    model = GiftCertificate

    # def get_context_data(self, slug=None, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['vehicle_type'] = VehicleType
    #     return context


class GiftCertificateStatusView(NavMenuMixin, UpdateView):
    template_name = 'front_site/gift_certificate_status.html'
    model = GiftCertificate
    fields = '__all__'

    def get_object(self, queryset=None):
        try:
            self.object = GiftCertificate.objects.get(tag=self.kwargs['tag'])
        except GiftCertificate.DoesNotExist:
            raise Http404
