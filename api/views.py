import datetime
import logging
import pytz
import requests
import stripe
from stripe.error import CardError

from rest_framework import viewsets, mixins, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from rest_framework.permissions import BasePermission
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action

from django.conf import settings
from django.urls import reverse_lazy, reverse
from django.db import IntegrityError
from django.db.models import Q
from django.contrib.auth import authenticate, login
from django.http import Http404, HttpResponseRedirect
from django.forms.models import model_to_dict

from sales.forms import (
    ReservationRentalDetailsForm, ReservationRentalPaymentForm, ReservationRentalLoginForm,
    PerformanceExperienceDetailsForm, PerformanceExperiencePaymentForm, PerformanceExperienceLoginForm,
    JoyRideDetailsForm, JoyRidePaymentForm, JoyRideLoginForm,
    GiftCertificateForm,
)
from marketing.forms import NewsletterSubscribeForm
from customer_portal.forms import ReservationCustomerInfoForm
from sales.models import BaseReservation, Reservation, Rental, TaxRate, generate_code
from sales.tasks import send_email
from sales.calculators import PriceCalculator
from sales.enums import CC2_ERROR_PARAM_MAP
from sales.models import Card
from users.models import User, Customer, Employee, generate_password
from fleet.models import Vehicle, VehicleMarketing, VehiclePicture
from api.serializers import (
    VehicleSerializer, VehicleDetailSerializer, CustomerSearchSerializer, ScheduleConflictSerializer,
    TaxRateFetchSerializer, CardSerializer
)
from sales.views import ReservationMixin

logger = logging.getLogger(__name__)

customer_fields = (
    'first_name', 'last_name', 'mobile_phone', 'home_phone', 'work_phone', 'fax', 'cc_number', 'cc_exp_yr',
    'cc_exp_mo', 'cc_cvv', 'cc_phone', 'address_line_1', 'address_line_2', 'city', 'state', 'zip'
)


class HasReservationsAccess(BasePermission):

    def has_permission(self, request, view):
        try:
            return bool(request.user and request.user.employee and request.user.employee.reservations_access)
        except Employee.DoesNotExist:
            return False


class GetVehiclesView(APIView):

    def get(self, request):
        vehicles = VehicleMarketing.objects.all()
        serializer = VehicleSerializer(vehicles, many=True)
        return Response(serializer.data)


class GetVehicleView(APIView):

    def get(self, request, vehicle_id):
        try:
            vehicle = VehicleMarketing.objects.get(pk=vehicle_id)
        except VehicleMarketing.DoesNotExist:
            raise Http404
        serializer = VehicleDetailSerializer(vehicle)
        return Response({'vehicle': serializer.data})


# 1st phase form; gathers basic rental details (vehicle date in/out, extra miles, etc)

class ValidateRentalDetailsView(APIView):

    # authentication_classes = ()
    # permission_classes = ()

    def post(self, request):
        form = ReservationRentalDetailsForm(request.POST)
        print(form.data)
        print(form.is_valid())
        print(form.errors.as_json())
        response = {
            'success': form.is_valid(),
            'errors': form.errors,
            'errors_html': form.errors.as_ul(),
            'customer_id': form.customer.id if form.customer else None,
            'price_data': form.price_data,
            'delivery_required': form.cleaned_data['delivery_required'],
        }
        return Response(response)


# 2nd phase form; handles either new customers (with CC details) or returning (with login creds)

class ValidateRentalPaymentView(ReservationMixin, APIView):
    form_class = ReservationRentalPaymentForm
    reservation_type = 'rental'

    def get_customer_site_url(self, confirmation_code):
        return reverse('customer_portal:confirm-reservation', kwargs={'confirmation_code': confirmation_code}),


class ValidateRentalLoginView(ValidateRentalPaymentView):
    authentication_classes = (SessionAuthentication,)
    form_class = ReservationRentalLoginForm


# Customer Portal confirmation of rental details (fill in insurance/license/2nd card/etc)

class ValidateRentalConfirmView(APIView):

    # authentication_classes = ()
    authentication_classes = (SessionAuthentication,)
    # permission_classes = ()
    form_type = None

    def post(self, request, *args, **kwargs):
        confirmation_code = request.POST.get('confirmation_code')
        try:
            reservation = BaseReservation.objects.get(confirmation_code=confirmation_code, customer=self.request.user.customer)
        except BaseReservation.DoesNotExist:
            raise Http404

        form = ReservationCustomerInfoForm(request.POST, instance=reservation.customer, confirmation_code=confirmation_code)
        print(form.data)
        print(self.form_type)
        print(form.is_valid())
        print(form.errors.as_json())
        if not form.is_valid():
            return Response({
                'success': False,
                'errors': form.errors,
            })

        # Save the rental confirmation, and handle Stripe card error on CC2 here
        try:
            form.save()
        except CardError as e:
            form.add_error(CC2_ERROR_PARAM_MAP.get(e.param), e.user_message)
            return Response({
                'success': False,
                'errors': form.errors,
            })

        if form.cleaned_data['cc2_instructions']:
            reservation.customer_notes += '\n\n' + form.cleaned_data['cc2_instructions']
            reservation.save()

        response = {
            'success': True,
            'reservation_type': 'rental',
            'customer_site_url': reverse('customer_portal:confirm-reservation', kwargs={'confirmation_code': confirmation_code}),
        }
        return Response(response)


# Joy Ride

class ValidateJoyRideDetailsView(APIView):

    # authentication_classes = ()
    # permission_classes = ()

    def post(self, request):
        form = JoyRideDetailsForm(request.POST)
        print(form.data)
        print(form.is_valid())
        print(form.errors.as_json())
        response = {
            'success': form.is_valid(),
            'errors': form.errors,
            'errors_html': form.errors.as_ul(),
            'customer_id': form.customer.id if form.customer else None,
            'price_data': form.price_data,
            # 'delivery_required': form.cleaned_data['delivery_required'],
        }
        return Response(response)


class ValidateJoyRidePaymentView(ReservationMixin, APIView):
    form_class = JoyRidePaymentForm
    reservation_type = 'joyride'

    def get_customer_site_url(self, confirmation_code):
        return reverse('customer_portal:joyride-confirm', kwargs={'confirmation_code': confirmation_code}),


class ValidateJoyRideLoginView(ValidateJoyRidePaymentView):
    authentication_classes = (SessionAuthentication,)
    form_class = JoyRideLoginForm


# Performance Experience

class ValidatePerformanceExperienceDetailsView(APIView):

    # authentication_classes = ()
    # permission_classes = ()

    def post(self, request):
        form = PerformanceExperienceDetailsForm(request.POST)
        print(form.data)
        print(form.is_valid())
        print(form.errors.as_json())
        response = {
            'success': form.is_valid(),
            'errors': form.errors,
            'errors_html': form.errors.as_ul(),
            'customer_id': form.customer.id if form.customer else None,
            'price_data': form.price_data,
            # 'delivery_required': form.cleaned_data['delivery_required'],
        }
        return Response(response)


class ValidatePerformanceExperiencePaymentView(ReservationMixin, APIView):
    form_class = PerformanceExperiencePaymentForm
    reservation_type = 'perfexp'

    def get_customer_site_url(self, confirmation_code):
        return reverse('customer_portal:perfexp-confirm', kwargs={'confirmation_code': confirmation_code}),


class ValidatePerformanceExperienceLoginView(ValidatePerformanceExperiencePaymentView):
    authentication_classes = (SessionAuthentication,)
    form_class = PerformanceExperienceLoginForm


# Newsletter

class ValidateNewsletterSubscriptionView(APIView):

    # authentication_classes = ()
    # permission_classes = ()

    # form_type is passed in via the url pattern in urls.py as a kwarg to .as_view()
    form_type = None

    def verify_recaptcha(self, recaptcha_response):
        payload = {
            'secret': settings.RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response,
        }
        return requests.post(settings.RECAPTCHA_VERIFY_URL, data=payload)

    def post(self, request):
        # form_class = self._get_form_class()
        form = NewsletterSubscribeForm(request.POST)
        # form = form_class(request.POST)
        print(form.data)
        print(self.form_type)
        print(form.is_valid())
        print(form.errors.as_json())
        if not form.is_valid():
            return Response({
                'success': False,
                'errors': form.errors,
            })

        recaptcha_response = self.verify_recaptcha(form.data.get('g-recaptcha-response'))
        recaptcha_result = recaptcha_response.json()
        if not recaptcha_result['success']:
            return Response({
                'success': False,
                'errors': ['ReCAPTCHA failure.'],
            })

        newsletter_subscription = form.save()

        email_subject = 'Performance Rentals Newsletter Confirmation'
        email_context = {
            'subscription': newsletter_subscription,
        }
        send_email(
            [form.cleaned_data['email']], email_subject, email_context,
            text_template='front_site/email/newsletter_subscribe_confirm.txt',
            html_template='front_site/email/newsletter_subscribe_confirm.html'
        )

        response = {
            'success': form.is_valid(),
            'errors': form.errors,
            'errors_html': form.errors.as_ul(),
            'success_url': reverse('newsletter-done'),
        }
        return Response(response)


# Gift Certificate

class ValidateGiftCertificateView(APIView):

    form_type = None

    def post(self, request):
        # form_class = self._get_form_class()
        form = GiftCertificateForm(request.POST)
        # form = form_class(request.POST)
        print(form.data)
        print(self.form_type)
        print(form.is_valid())
        print(form.errors.as_json())
        if not form.is_valid():
            return Response({
                'success': False,
                'errors': form.errors,
            })

        gift_certificate = form.save()

        response = {
            'success': form.is_valid(),
            'errors': form.errors,
            'errors_html': form.errors.as_ul(),
            'reservation_type': 'gift',
            'success_url': reverse('gift-certificate-status', kwargs={'tag': gift_certificate.tag}),
        }
        return Response(response)


# Consignment

class ConsignmentReserveView(APIView):
    pass


# Single entrypoint to handle all API calls from mobile app
class LegacyPostView(APIView):

    def post(self, request):
        method = request.POST.get('method')

        if method == 'getVehicles':
            view = GetVehiclesView()
            return view.get(request)

        # TODO: 'getVehicle'
        # TODO: 'getVehiclePics'
        # TODO: 'validateRentalIdentity'
        # TODO: 'validateRentalPayment'
        # TODO: 'getNews'

        return Response({})


class LegacyVehicleMobileThumbnailView(APIView):

    def get(self, request, vehicle_id):
        try:
            vehicle_marketing = VehicleMarketing.objects.get(pk=vehicle_id)
        except VehicleMarketing.DoesNotExist:
            raise Http404
        return HttpResponseRedirect(vehicle_marketing.mobile_thumbnail_image.url)


class LegacyVehiclePicView(APIView):

    def get(self, request, vehicle_picture_id):
        try:
            vehicle_picture = VehiclePicture.objects.get(pk=vehicle_picture_id)
        except VehiclePicture.DoesNotExist:
            raise Http404
        return HttpResponseRedirect(vehicle_picture.image.url)


# Stripe payment endpoints

# This is all from Pikpac; needs to be reworked for customer-facing functionality during a reservation
# (use the Stripe class in sales.stripe)
class CardViewSet(viewsets.ModelViewSet):

    serializer_class = CardSerializer

    def get_queryset(self):
        return Card.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def get_token(self, request):
        logger.info(request.GET)
        stripe.api_key = settings.STRIPE_SECRET_KEY

        token = stripe.Token.retrieve(request.GET['token'])

        return Response(token, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def add(self, request):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        logger.info(request.data)

        try:
            stripe_card = stripe.Customer.create_source(
                request.user.stripe_customer,
                source=request.data['token']['id'],
                # source='tok_chargeCustomerFail',
            )
        except (stripe.error.CardError, stripe.error.InvalidRequestError) as e:
            body = e.json_body
            err = body.get('error', {})

            logger.info("Status is: %s" % e.http_status)
            logger.info("Type is: %s" % err.get('type'))
            logger.info("Code is: %s" % err.get('code'))
            # param is '' in this case
            logger.info("Param is: %s" % err.get('param'))
            logger.info("Message is: %s" % err.get('message'))

            return Response({'status': 'error', 'error': err})

        card = Card.objects.create(
            stripe_card=stripe_card.id,
            user=request.user,
            brand=stripe_card.brand,
            last_4=stripe_card.last4,
            exp_month=stripe_card.exp_month,
            exp_year=stripe_card.exp_year,
            fingerprint=stripe_card.fingerprint,
        )
        request.user.default_card = card
        request.user.save()
        serializer = self.get_serializer(data=model_to_dict(card))
        serializer.is_valid(raise_exception=True)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


# Backoffice API endpoints (authenticated)

class SearchCustomersView(APIView):

    authentication_classes = (SessionAuthentication,)
    permission_classes = (HasReservationsAccess,)

    def get(self, request):
        term = request.GET.get('term', '')
        if len(term) < 2:
            return Response([])
        customers = Customer.objects.filter(
            Q(first_name__icontains=term) | Q(last_name__icontains=term) | Q(user__email__icontains=term)
        )
        serializer = CustomerSearchSerializer(customers, many=True)
        return Response(serializer.data)


class TaxRateByZipView(APIView):

    authentication_classes = (SessionAuthentication,)
    permission_classes = (HasReservationsAccess,)

    def post(self, request):
        serializer = TaxRateFetchSerializer(data=request.POST)
        if not serializer.is_valid():
            return Response({'success': False, 'error': 'No ZIP code specified'})

        tax_zip = serializer.data['zip']
        force_refresh = serializer.data['force_refresh']

        if force_refresh:
            for tax_rate in TaxRate.objects.filter(postal_code=tax_zip):
                tax_rate.update()

        price_calculator = PriceCalculator(coupon_code=None, email=None, tax_zip=tax_zip, effective_date=None)
        tax_rate = price_calculator.tax_rate
        return Response({
            'success': True,
            'tax_rate': float(tax_rate.total_rate_as_percent),
            'detail': tax_rate.detail,
        })


class CheckScheduleConflictView(APIView):

    authentication_classes = (SessionAuthentication,)
    permission_classes = (HasReservationsAccess,)

    def post(self, request):
        try:
            out_at_date = datetime.datetime.strptime(request.POST.get('out_at_date'), '%m/%d/%Y').date()
            out_at_time = datetime.datetime.strptime(request.POST.get('out_at_time'), '%H:%M').time()
            out_at = datetime.datetime.combine(out_at_date, out_at_time).astimezone(pytz.timezone(settings.TIME_ZONE))

            back_at_date = datetime.datetime.strptime(request.POST.get('back_at_date'), '%m/%d/%Y').date()
            back_at_time = datetime.datetime.strptime(request.POST.get('back_at_time'), '%H:%M').time()
            back_at = datetime.datetime.combine(back_at_date, back_at_time).astimezone(pytz.timezone(settings.TIME_ZONE))
        except ValueError:
            return Response({'success': False, 'error': 'Out/back dates not set'})

        vehicle = Vehicle.objects.get(pk=request.POST.get('vehicle_id'))

        conflicts = BaseReservation.objects.filter(vehicle=vehicle, back_at__gte=out_at, out_at__lte=back_at)
        exclude_id = request.POST.get('reservation_id') or request.POST.get('rental_id')
        conflicts = conflicts.exclude(pk=exclude_id)

        serializer = ScheduleConflictSerializer(conflicts, many=True)

        return Response({
            'success': True,
            'make': vehicle.make,
            'model': vehicle.model,
            'conflicts': serializer.data
        })


class SendInsuranceAuthView(APIView):

    authentication_classes = (SessionAuthentication,)
    permission_classes = (HasReservationsAccess,)

    def post(self, request):
        customer_id = request.POST.get('customer_id')
        try:
            customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            raise Http404

        # TODO: Send templated email

        return Response({
            'success': True,
        })


class SendWelcomeEmailView(APIView):

    authentication_classes = (SessionAuthentication,)
    permission_classes = (HasReservationsAccess,)

    def post(self, request):
        reservation_id = request.POST.get('reservation_id')
        try:
            reservation = BaseReservation.objects.get(pk=reservation_id)
        except Reservation.DoesNotExist:
            raise Http404

        # TODO: Send templated email

        return Response({
            'success': True,
            'confirmation_code': reservation.confirmation_code,
        })
