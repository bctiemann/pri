import datetime
import logging
from stripe.error import CardError

from django.conf import settings
from django.views.generic import TemplateView, FormView, CreateView, UpdateView
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import reverse
from django.db import IntegrityError
from django.contrib.auth import authenticate, login, logout
from django import forms
from django.utils import timezone

from rest_framework.response import Response
from rest_framework.exceptions import APIException

from users.models import User, Customer
from sales.forms import (
    ReservationRentalDetailsForm, ReservationRentalPaymentForm, ReservationRentalLoginForm,
    PerformanceExperienceDetailsForm, PerformanceExperiencePaymentForm, PerformanceExperienceLoginForm,
    JoyRideDetailsForm, JoyRidePaymentForm, JoyRideLoginForm,
    GiftCertificateForm, AdHocPaymentForm
)
from sales.models import GiftCertificate, AdHocPayment, IPBan, generate_code
from sales.enums import ServiceType
from sales.constants import GIFT_CERTIFICATE_TEXT
from marketing.views import NavMenuMixin
from fleet.models import Vehicle, VehicleMarketing, VehicleType, VehicleStatus
from pri.pdf import PDFView

customer_fields = (
    'first_name', 'last_name', 'mobile_phone', 'home_phone', 'work_phone', 'fax', 'cc_number', 'cc_exp_yr',
    'cc_exp_mo', 'cc_cvv', 'cc_phone', 'address_line_1', 'address_line_2', 'city', 'state', 'zip'
)

logger = logging.getLogger(__name__)


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
        # form.customer is just Customer filtered by the given email; may or may not be authenticated as
        # the linked User.
        if form.customer:

            if request.user.is_authenticated and request.user.customer != form.customer:
                # User was already logged in and is now using new credentials. Log them out so they're forced to
                # re-auth.
                logout(request)

            # Re-auth even if user is already authenticated.
            if authenticate(request, username=form.customer.email, password=form.cleaned_data.get('password')):
                login(request, form.customer.user)
                return form.customer

            # Only way to get here is if password is incorrect for an existing user's email.
            raise ValueError('Incorrect password.')

        else:
            # There is no Customer matching the submitted email address, so we have to decide what to do with it.

            new_password = form.cleaned_data.get('password_new')

            # If there is no password, it means the user changed the email address to that of an existing user after
            # submitting an unknown email in the details form. Ideally this should be prevented in the front-end.
            if not new_password:
                raise ValueError('Email address was changed. Please refresh the page and try again.')

            # We have already checked whether a Customer exists that is linked to a User with the given email. Now
            # we have to check whether a bare User exists with that email. If we do, this means we have a data problem.
            # This might occur if we deleted a Customer but did not delete the linked User.
            # Log the email and return an error to the customer.
            try:
                user = User.objects.create_user(form.cleaned_data['email'], password=new_password)
            except IntegrityError:
                logger.warning(f"Customer submitted reservation with email {form.cleaned_data['email']} which matches a User with no Customer attached.")
                raise ValueError('User data error occurred.')

            # Create the customer object. Stripe cards are not registered until the Customer has an id (has been saved).
            customer_kwargs = {key: form.cleaned_data.get(key) for key in customer_fields}
            customer = Customer.objects.create(
                user=user,
                registration_ip=request.remote_ip,
                **customer_kwargs,
            )
            # Save a second time to register Stripe cards
            customer.save()

            # Now login as the resolved user
            login(request, user)

        return customer

    def create_reservation(self, request, form=None):
        form = form or self.form_class(request.POST)
        logger.debug(form.data)
        logger.debug(form.is_valid())
        logger.debug(form.errors.as_json())

        # CAPTCHA is checked as part of the form validation; if that fails, errors are returned here
        if not form.is_valid():
            return {
                'success': False,
                'errors': form.errors,
            }

        # Check IP here. If more than 2 customers created with the same IP in the last 10 minutes, create an IPBan.
        if settings.REGISTRATION_FROM_SAME_IP_AUTO_BLOCK:
            ten_minutes_ago = timezone.now() - datetime.timedelta(
                minutes=settings.REGISTRATION_FROM_SAME_IP_INTERVAL_MINS
            )
            check_customers = Customer.objects.filter(created_at__gt=ten_minutes_ago, registration_ip=request.remote_ip)
            if check_customers.count() > settings.REGISTRATION_FROM_SAME_IP_COUNT - 1:
                IPBan.objects.create(ip_address=request.remote_ip, prefix_bits=32)

        # IP-based block list will send client to the honeypot success page and short-circuit all further processing.
        # Can be set globally (in settings.py or env.yaml) or by creating an IPBan, or by using the "global kill switch"
        # (a synonym for an IPBan of 0.0.0.0/0).
        kill_switch = settings.KILL_SWITCH or IPBan.global_kill_switch or IPBan.ip_is_banned(request.remote_ip)
        if kill_switch:
            return {
                'success': True,
                'reservation_type': self.reservation_type,
                'confirmation_code': generate_code(self.reservation_type),
                'customer_site_url': self.get_honeypot_url(form=form),
            }

        # Passed abuse checks; now proceed with validating the login credentials.

        # Create Customer or login existing user
        try:
            customer = self._get_login_customer(request, form)
        except ValueError as e:
            error_msg = str(e)
            return {
                'success': False,
                'error': error_msg,
                'errors': {
                    'password': [error_msg],
                },
            }

        # Create Reservation

        reservation = form.save(commit=False)
        reservation.customer = customer

        # If rental, resolve vehicle
        if 'vehicle_marketing' in form.cleaned_data:
            reservation.vehicle = form.cleaned_data['vehicle_marketing'].vehicle

        # This will simply return an opaque "system error" to the front-end. Ideally should return a helpful message,
        # but also ideally this will never fail due to a confirmation_code collision.
        try:
            reservation.save()
        except IntegrityError as e:
            raise APIException(detail=e, code='collision')

        reservation.send_welcome_email()

        return {
            'success': form.is_valid(),
            'error': form.get_error(),
            'errors': form.errors,
            'errors_html': form.errors.as_ul(),
            'customer_id': reservation.customer.id,
            'reservation_id': reservation.id,
            'reservation_type': self.reservation_type,
            'confirmation_code': reservation.confirmation_code,
            'customer_site_url': self.get_customer_site_url(confirmation_code=reservation.confirmation_code),
        }

    def get_customer_site_url(self, **kwargs):
        raise NotImplementedError

    def get_honeypot_url(self, **kwargs):
        raise NotImplementedError

    def get_error(self, form):
        if form.is_valid():
            return None
        if form.non_field_errors():
            return form.non_field_errors()[0]
        return f'{list(form.errors.keys())[0]}: {list(form.errors.values())[0][0]}'


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
            if field in form.fields:
                form[field].field.widget.attrs.setdefault('class', '')
                form[field].field.widget.attrs['class'] += ' field-error'
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        form = kwargs.get('form')
        form_type = kwargs.get('form_type')
        context = super().get_context_data(**kwargs)
        context['form_type'] = form_type or 'details'
        if form:
            context['price_data'] = form.price_data if form else None
        return context


class VehicleMixin:

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data(**kwargs))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs.get('slug')
        # We filter() rather than get() because vehicle_marketing.slug is not unique (we may have multiple of the
        # same vehicle)
        context['vehicle'] = VehicleMarketing.objects.ready().filter(slug__iexact=slug).first()
        if not context['vehicle']:
            raise Http404
        return context


# Reservation/Rental

# This template is rendered with three forms: details (phase 1), payment (phase 2 for new user), and login (phase 2 for
# returning user). All three forms have different validation needs and field sets.
class ReserveView(NavMenuMixin, PaymentLoginFormMixin, ReservationMixin, NoJSFlowMixin, VehicleMixin, FormView):
    template_name = 'front_site/reserve/reserve.html'
    form_class = ReservationRentalDetailsForm
    payment_form_class = ReservationRentalPaymentForm
    login_form_class = ReservationRentalLoginForm
    form_type = 'details'
    reservation_type = ServiceType.RENTAL

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
        context['price_data'] = form.price_data if form else None
        return context


class ReserveHoneypotView(NavMenuMixin, VehicleMixin, TemplateView):
    template_name = 'front_site/reserve/honeypot.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['confirmation_code'] = generate_code(ServiceType.RENTAL)
        return context


# Performance Experience

class PerformanceExperienceView(NavMenuMixin, PaymentLoginFormMixin, ReservationMixin, NoJSFlowMixin, FormView):
    template_name = 'front_site/performance_experience/reserve.html'
    form_class = PerformanceExperienceDetailsForm
    payment_form_class = PerformanceExperiencePaymentForm
    login_form_class = PerformanceExperienceLoginForm
    reservation_type = ServiceType.PERFORMANCE_EXPERIENCE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['vehicle_type'] = VehicleType
        context['reservation_type'] = self.reservation_type
        return context

    def get_customer_site_url(self, confirmation_code):
        return reverse('customer_portal:perfexp-confirm', kwargs={'confirmation_code': confirmation_code})

    def get_honeypot_url(self, **kwargs):
        return reverse('performance-experience-honeypot')


class PerformanceExperienceLoginFormView(PerformanceExperienceView):
    template_name = 'front_site/includes/login_form.html'
    form_class = PerformanceExperienceLoginForm


class PerformanceExperiencePaymentFormView(PerformanceExperienceView):
    template_name = 'front_site/includes/payment_form.html'
    form_class = PerformanceExperiencePaymentForm


class PerformanceExperiencePriceBreakdownView(FormView):
    template_name = 'front_site/performance_experience/price_breakdown.html'
    form_class = PerformanceExperienceDetailsForm

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.render_to_response(self.get_context_data(form=form, **kwargs))

    def get_context_data(self, slug=None, form=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['price_data'] = form.price_data if form else None
        return context


class PerformanceExperienceHoneypotView(NavMenuMixin, TemplateView):
    template_name = 'front_site/performance_experience/honeypot.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['confirmation_code'] = generate_code(ServiceType.PERFORMANCE_EXPERIENCE)
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
        context['reservation_type'] = self.reservation_type
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
        context['price_data'] = form.price_data if form else None
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


class GiftCertificateStatusView(NavMenuMixin, UpdateView):
    template_name = 'front_site/gift_certificate_status.html'
    model = GiftCertificate
    fields = '__all__'

    def get_object(self, queryset=None):
        try:
            self.object = GiftCertificate.objects.get(tag=self.kwargs['tag'])
        except GiftCertificate.DoesNotExist:
            raise Http404


class GiftCertificatePDFView(PDFView):
    template_name = 'pdf/gift_certificate.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['gift_certificate'] = GiftCertificate.objects.get(tag=self.kwargs['tag'], is_paid=True)
            context['gift_certificate_text'] = GIFT_CERTIFICATE_TEXT
        except GiftCertificate.DoesNotExist:
            raise Http404
        context['company_phone'] = settings.COMPANY_PHONE
        return context


# AdHoc Payments (SubPay)

class AdHocPaymentView(NavMenuMixin, UpdateView):
    template_name = 'front_site/payment/payment.html'
    model = AdHocPayment
    form_class = AdHocPaymentForm

    def get_object(self, queryset=None):
        try:
            return AdHocPayment.objects.get(confirmation_code=self.kwargs['confirmation_code'])
        except AdHocPayment.DoesNotExist:
            raise Http404

    # Should not be called -- only on non-JS flow
    def form_valid(self, form):
        payment = form.save(commit=False)
        payment.is_submitted = True
        payment.submitted_at = timezone.now()
        payment.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('adhoc-payment', kwargs={'confirmation_code': self.object.confirmation_code})


class AdHocPaymentDoneView(NavMenuMixin, TemplateView):
    template_name = 'front_site/payment/done.html'
