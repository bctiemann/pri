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
from django.http import Http404, HttpResponseRedirect, HttpResponseBadRequest
from django.forms.models import model_to_dict
from django.utils import timezone

from sales.forms import (
    ReservationRentalDetailsForm, ReservationRentalPaymentForm, ReservationRentalLoginForm,
    PerformanceExperienceDetailsForm, PerformanceExperiencePaymentForm, PerformanceExperienceLoginForm,
    JoyRideDetailsForm, JoyRidePaymentForm, JoyRideLoginForm,
    GiftCertificateForm, AdHocPaymentForm
)
from marketing.forms import NewsletterSubscribeForm, NewsletterUnsubscribeForm
from marketing.models import NewsletterSubscription, NewsItem
from customer_portal.forms import ReservationCustomerInfoForm
from sales.models import BaseReservation, Reservation, Rental, TaxRate, AdHocPayment, GiftCertificate, generate_code
from sales.tasks import send_email
from sales.calculators import PriceCalculator
from sales.enums import CC2_ERROR_PARAM_MAP, ServiceType
from sales.models import Card
from users.models import User, Customer, Employee, generate_password
from fleet.models import Vehicle, VehicleMarketing, VehiclePicture
from api.serializers import (
    VehicleSerializer, VehicleDetailSerializer, VehiclePicsSerializer, CustomerSearchSerializer,
    ScheduleConflictSerializer, TaxRateFetchSerializer, CardSerializer, NewsItemSerializer
)
from sales.views import ReservationMixin

logger = logging.getLogger(__name__)


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


class GetVehiclePicsView(APIView):

    def get(self, request, vehicle_id):
        try:
            vehicle = VehicleMarketing.objects.get(pk=vehicle_id)
        except VehicleMarketing.DoesNotExist:
            raise Http404
        serializer = VehiclePicsSerializer(vehicle.pics, many=True)
        return Response(serializer.data)


class GetNewsView(APIView):

    def get(self, request):
        news_items = NewsItem.objects.all()
        serializer = NewsItemSerializer(news_items, many=True)
        return Response(serializer.data)


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

    def post_legacy(self, request, payload):
        form = ReservationRentalDetailsForm(payload)
        print(form.data)
        print(form.is_valid())
        print(form.errors.as_json())
        vehicle_marketing = form.cleaned_data.get('vehicle_marketing')
        response = {
            'success': form.is_valid(),
            'error': form.get_error(),
            'price_data': form.price_data,
            "tax_amt": form.price_data.get('tax_amount'),
            "total_w_tax": form.price_data.get('total_with_tax'),
            "reservation_deposit": form.price_data.get('reservation_deposit'),
            "multi_day_discount_pct": form.price_data.get('multi_day_discount_pct'),
            "extra_miles": form.price_data.get('extra_miles'),
            "fieldErrors": form.errors,
            "deposit": vehicle_marketing.security_deposit if vehicle_marketing else None,
            "rental_duration": form.rental_duration_hours,
            "tcostRaw": form.price_data.get('base_price'),
            "numdrivers": int(form.cleaned_data['drivers']),
            "customer_discount": form.price_data.get('specific_discount'),
            "customer_discount_pct": 0,
            "tcost": form.price_data.get('post_multi_day_discount_subtotal'),
            "delivery": int(form.cleaned_data['delivery_required']),
            "customerid": form.customer.id if form.customer else None,
            "numdays": form.num_days,
            "subtotal": form.price_data.get('subtotal'),
            "dateout_check": form.cleaned_data['out_at'],  # "June, 01 2023 09:30:00",
            "extra_miles_cost": form.price_data.get('extra_miles_cost'),
            "tax_rate": form.price_data.get('tax_rate', 0) * 100,
            "car_discount": form.price_data.get('coupon_discount'),
            "multi_day_discount": form.price_data.get('multi_day_discount'),
        }
        return Response(response)


# 2nd phase form; handles either new customers (with CC details) or returning (with login creds)

class ValidateRentalPaymentView(ReservationMixin, APIView):
    form_class = ReservationRentalPaymentForm
    reservation_type = ServiceType.RENTAL

    def post(self, request):
        reservation_result = self.create_reservation(request)
        return Response(reservation_result)

    def post_legacy(self, request, payload):
        form = self.form_class(payload)
        reservation_result = self.create_reservation(request, form=form)
        response = {
            'success': reservation_result.get('success'),
            'error': reservation_result.get('error'),
            'reservationid': reservation_result.get('reservation_id'),
            'customerid': reservation_result.get('customer_id'),
            'create_pass': None,
            'confcode': reservation_result.get('confirmation_code'),
            'custsite': reservation_result.get('customer_site_url'),
            'reservation_type': reservation_result.get('reservation_type'),
        }
        return Response(response)

    def get_customer_site_url(self, confirmation_code):
        return reverse('customer_portal:confirm-reservation', kwargs={'confirmation_code': confirmation_code})

    def get_honeypot_url(self, form=None, **kwargs):
        return reverse('reserve-honeypot', kwargs={'slug': form.vehicle.slug})


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
    reservation_type = ServiceType.JOY_RIDE

    def post(self, request):
        reservation_result = self.create_reservation(request)
        return Response(reservation_result)

    def get_customer_site_url(self, confirmation_code):
        return reverse('customer_portal:joyride-confirm', kwargs={'confirmation_code': confirmation_code})

    def get_honeypot_url(self, **kwargs):
        return reverse('joy-ride-honeypot')


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
    reservation_type = ServiceType.PERFORMANCE_EXPERIENCE

    def post(self, request):
        reservation_result = self.create_reservation(request)
        return Response(reservation_result)

    def get_customer_site_url(self, confirmation_code):
        return reverse('customer_portal:perfexp-confirm', kwargs={'confirmation_code': confirmation_code}),

    def get_honeypot_url(self, **kwargs):
        return reverse('performance-experience-honeypot')


class ValidatePerformanceExperienceLoginView(ValidatePerformanceExperiencePaymentView):
    authentication_classes = (SessionAuthentication,)
    form_class = PerformanceExperienceLoginForm


# Newsletter

# TODO: create subscribe_newsletter method in marketing.views, and call here and in NewsletterView
class ValidateNewsletterSubscriptionView(APIView):

    # authentication_classes = ()
    # permission_classes = ()

    # form_type is passed in via the url pattern in urls.py as a kwarg to .as_view()
    form_type = None

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

        # recaptcha_response = self.verify_recaptcha(form)
        # recaptcha_result = recaptcha_response.json()
        # if not recaptcha_result['success']:
        #     return Response({
        #         'success': False,
        #         'errors': ['ReCAPTCHA failure.'],
        #     })

        newsletter_subscription = form.save()

        email_subject = 'Performance Rentals Newsletter Confirmation'
        email_context = {
            'subscription': newsletter_subscription,
            'site_url': settings.SERVER_BASE_URL,
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


class ValidateNewsletterUnsubscriptionView(APIView):

    form_type = None

    def post(self, request):
        # form_class = self._get_form_class()
        form = NewsletterUnsubscribeForm(request.POST)
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

        subscriptions = NewsletterSubscription.objects.filter(email=form.cleaned_data['email'])
        subscriptions.delete()

        response = {
            'success': form.is_valid(),
            'errors': form.errors,
            'errors_html': form.errors.as_ul(),
            'success_url': reverse('newsletter-unsubscribe-done'),
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

        email_subject = 'PRI Gift Certificate Confirmation'
        email_context = {
            'gift_certificate': gift_certificate,
            'site_url': settings.SERVER_BASE_URL,
            'company_phone': settings.COMPANY_PHONE,
            'site_email': settings.SITE_EMAIL,
        }
        send_email(
            [gift_certificate.email], email_subject, email_context,
            text_template='front_site/email/gift_cert_confirm.txt',
            html_template='front_site/email/gift_cert_confirm.html',
        )

        response = {
            'success': form.is_valid(),
            'errors': form.errors,
            'errors_html': form.errors.as_ul(),
            'reservation_type': 'gift',
            'success_url': reverse('gift-certificate-status', kwargs={'tag': gift_certificate.tag}),
        }
        return Response(response)


# Ad-hoc Payment

class ValidateAdHocPaymentView(APIView):

    form_type = None

    def post(self, request):
        # form_class = self._get_form_class()
        payment = AdHocPayment.objects.get(confirmation_code=request.POST['confirmation_code'])
        form_kwargs = {'instance': payment, 'data': request.POST}
        form = AdHocPaymentForm(**form_kwargs)
        print(form.data)
        print(self.form_type)
        print(form.is_valid())
        print(form.errors.as_json())
        if not form.is_valid():
            return Response({
                'success': False,
                'errors': form.errors,
            })

        payment = form.save(commit=False)
        payment.is_submitted = True
        payment.submitted_at = timezone.now()
        payment.save()

        email_subject = 'PRI SubPay - Submitted'
        email_context = {
            'payment': payment,
        }
        send_email(
            [settings.SITE_EMAIL], email_subject, email_context,
            text_template='front_site/email/adhoc_payment_submitted.txt',
            html_template='front_site/email/adhoc_payment_submitted.html',
            from_address=settings.SALES_EMAIL,
        )

        response = {
            'success': form.is_valid(),
            'errors': form.errors,
            'errors_html': form.errors.as_ul(),
            'reservation_type': 'subpay',
            'success_url': reverse('adhoc-payment-done', kwargs={'confirmation_code': form.instance.confirmation_code}),
        }
        return Response(response)


# TODO: wtf is this
class ValidateSurveyResponseView(APIView):

    form_type = None

    def post(self, request):
        response = {
            'success': form.is_valid(),
            'errors': form.errors,
            'errors_html': form.errors.as_ul(),
            'reservation_type': 'gift',
            'success_url': reverse('adhoc-payment-done', kwargs={'confirmation_code': form.instance.confirmation_code}),
        }
        return Response(response)


# Consignment

class ConsignmentReserveView(APIView):
    pass


# Single entrypoint to handle all API calls from mobile app
# TODO: Rebuild mobile app to use bespoke API endpoints directly and remove the ajax_post.cfm url
class LegacyPostView(APIView):

    def post(self, request):
        method = request.POST.get('method')

        if method == 'getVehicles':
            view = GetVehiclesView()
            return view.get(request)

        if method == 'getVehicle':
            view = GetVehicleView()
            vehicle_id = request.POST.get('vehicleid')
            if not vehicle_id.isdigit():
                return HttpResponseBadRequest()
            return view.get(request, vehicle_id=vehicle_id)

        if method == 'getVehiclePics':
            view = GetVehiclePicsView()
            vehicle_id = request.POST.get('vehicleid')
            if not vehicle_id.isdigit():
                return HttpResponseBadRequest()
            return view.get(request, vehicle_id=vehicle_id)

        if method == 'validateRentalIdentity':
            view = ValidateRentalDetailsView()
            payload = dict(
                email=request.POST.get('email'),
                vehicle_marketing=request.POST.get('vehicleid'),
                out_date=request.POST.get('dateout'),
                out_time=request.POST.get('dateouttime'),
                back_date=request.POST.get('dateback'),
                back_time=request.POST.get('datebacktime'),
                delivery_required=request.POST.get('delivery'),
                delivery_zip=request.POST.get('deliveryzip'),
                extra_miles=request.POST.get('extramiles'),
                coupon=request.POST.get('coupon'),
                drivers=request.POST.get('drivers'),
            )
            return view.post_legacy(request, payload)

        if method == 'validateRentalPayment':
            # If the first-phase form collected a known email, the app prompts for login_pass. If this is not
            # present in this second-phase form data, we use the payment view/form which creates a new customer
            # and payment data, and we assign a randomly generated password (the customer must reset it using
            # the Forgot mechanism at present). Otherwise, we use the login form which uses the entered login_pass.
            if request.POST.get('login_pass'):
                view = ValidateRentalLoginView()
            else:
                view = ValidateRentalPaymentView()

            # Hard-coded app key which must be present in the payload for this final form submit
            if request.POST.get('vk') != settings.MOBILE_KEY:
                return Response({'success': False})

            new_password = generate_password()
            payload = dict(
                reservation_type=request.POST.get('reservation_type'),
                vehicle_marketing=request.POST.get('vehicleid'),
                customer=request.POST.get('customerid'),
                email=request.POST.get('email'),
                password=request.POST.get('login_pass'),
                out_date=request.POST.get('dateout'),
                out_time=request.POST.get('dateouttime'),
                back_date=request.POST.get('dateback'),
                back_time=request.POST.get('datebacktime'),
                delivery_required=request.POST.get('delivery'),
                delivery_zip=request.POST.get('deliveryzip'),
                extra_miles=request.POST.get('extramiles'),
                coupon=request.POST.get('coupon'),
                drivers=request.POST.get('drivers'),
                customer_notes=request.POST.get('notes'),
                first_name=request.POST.get('fname'),
                last_name=request.POST.get('lname'),
                mobile_phone=request.POST.get('mphone'),
                home_phone=request.POST.get('hphone'),
                work_phone=request.POST.get('wphone'),
                fax=request.POST.get('fax'),
                cc_number=request.POST.get('ccnum'),
                cc_exp_mo=request.POST.get('ccexpmo'),
                cc_exp_yr=request.POST.get('ccexpyr'),
                cc_cvv=request.POST.get('cccvv'),
                cc_phone=request.POST.get('cctel'),
                address_line_1=request.POST.get('addr'),
                city=request.POST.get('city'),
                state=request.POST.get('state'),
                zip=request.POST.get('zip'),
                password_new=new_password,
                password_repeat=new_password,
            )
            return view.post_legacy(request, payload)

        if method == 'getNews':
            view = GetNewsView()
            return view.get(request)

        return HttpResponseBadRequest()


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

        # Send email with PDF attachment to customer
        email_subject = 'Performance Rentals Insurance Authorization Form'
        email_from = f'{settings.RESERVATIONS_EMAIL} (Performance Rentals Reservations)'
        email_context = {
            'customer': customer,
            'company_phone': settings.COMPANY_PHONE,
            'company_fax': settings.COMPANY_FAX,
            'site_email': settings.SITE_EMAIL,
        }

        # TODO: Update PDF with current address/info, and make editable
        # TODO: Generate PDF dynamically
        attachments = []
        with open(f'{settings.BASE_DIR}/templates/attachments/PRI-infoauth.pdf', 'rb') as file:
            attachment_data = file.read()
        attachments.append({'filename': 'PRI-infoauth.pdf', 'content': attachment_data, 'mimetype': 'application/pdf'})

        send_email(
            [customer.email], email_subject, email_context,
            from_address=email_from,
            text_template='email/reservation_insurance.txt',
            html_template='email/reservation_insurance.html',
            attachments=attachments,
        )

        # Send echo email to administration
        email_subject = 'Insurance Form Sent'

        send_email(
            [settings.SITE_EMAIL], email_subject, email_context,
            from_address=email_from,
            text_template='email/reservation_insurance_echo.txt',
            html_template='email/reservation_insurance_echo.txt',
        )

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

        reservation.send_welcome_email()

        return Response({
            'success': True,
            'confirmation_code': reservation.confirmation_code,
        })


class SendGiftCertEmailView(APIView):

    authentication_classes = (SessionAuthentication,)
    permission_classes = (HasReservationsAccess,)

    def post(self, request):
        giftcertificate_id = request.POST.get('giftcertificate_id')
        try:
            giftcertificate = GiftCertificate.objects.get(pk=giftcertificate_id)
        except GiftCertificate.DoesNotExist:
            raise Http404

        giftcertificate.send_download_email()

        return Response({
            'success': True,
        })
