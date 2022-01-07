import datetime
import logging
import requests

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from rest_framework.permissions import BasePermission
from rest_framework.authentication import SessionAuthentication

from django.conf import settings
from django.urls import reverse_lazy, reverse
from django.db import IntegrityError
from django.db.models import Q
from django.contrib.auth import authenticate, login
from django.http import Http404, HttpResponseRedirect

from sales.forms import ReservationRentalDetailsForm, ReservationRentalPaymentForm, ReservationRentalLoginForm
from marketing.forms import NewsletterSubscribeForm
from sales.models import BaseReservation, Reservation, Rental, generate_code
from sales.enums import ReservationType
from sales.tasks import send_email
from sales.utils import PriceCalculator
from users.models import User, Customer, Employee, generate_password
from fleet.models import Vehicle, VehicleMarketing, VehiclePicture
from api.serializers import VehicleSerializer, VehicleDetailSerializer, CustomerSearchSerializer, ScheduleConflictSerializer

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


class ValidateRentalPaymentView(APIView):

    # authentication_classes = ()
    # permission_classes = ()

    # form_type is passed in via the url pattern in urls.py as a kwarg to .as_view()
    form_type = None

    def _get_form_class(self):
        if self.form_type == 'payment':
            return ReservationRentalPaymentForm
        elif self.form_type == 'login':
            return ReservationRentalLoginForm

    @staticmethod
    def _get_login_customer(request, form):
        if form.customer:
            if authenticate(request, username=form.customer.email, password=form.cleaned_data['password']):
                login(request, form.customer.user)
                return form.customer
            # Only way to return None is if password is incorrect for an existing user's email
            return None
        else:
            # Create Customer object and login
            # TODO: Ensure that every User has a Customer attached, as providing an email of an unattached user will
            # try to create a new user which will fail the uniqueness constraint. Alternatively, do a get_or_create
            user = User.objects.create_user(form.cleaned_data['email'], password=generate_password())
            customer_kwargs = {key: form.cleaned_data.get(key) for key in form.customer_fields}
            customer = Customer.objects.create(
                user=user,
                **customer_kwargs,
            )
            login(request, user)
        return customer

    def post(self, request):
        form_class = self._get_form_class()
        # form = ReservationRentalDetailsForm(request.POST)
        form = form_class(request.POST)
        print(form.data)
        print(self.form_type)
        print(form.is_valid())
        print(form.errors.as_json())
        if not form.is_valid():
            return Response({
                'success': False,
                'errors': form.errors,
            })

        # Create Customer or login existing user
        customer = self._get_login_customer(request, form)
        if not customer:
            return Response({
                'success': False,
                'errors': {
                    'password': ['Incorrect password'],
                },
            })

        # Create Reservation

        # Generate a unique confirmation code.
        # Retry until successful or we run out of retries (increase retries_left if necessary)
        confirmation_code = None
        reservation = None
        retries_left = 5
        while not reservation and retries_left > 0:
            confirmation_code = generate_code(ReservationType.RENTAL.value)
            try:
                reservation = Reservation.objects.create(
                    confirmation_code=confirmation_code,
                    customer=customer,
                    vehicle=form.vehicle,

                )
            except IntegrityError:
                logger.warning(f'Confirmation code collision: {confirmation_code}')
                retries_left -= 1
        if not reservation:
            raise APIException(detail='Failed to generate a unique confirmation code.', code='collision')

        response = {
            'success': form.is_valid(),
            'errors': form.errors,
            'errors_html': form.errors.as_ul(),
            'reservation_type': 'rental',
            'customer_site_url': reverse('customer_portal:confirm-reservation', kwargs={'confirmation_code': confirmation_code}),
        }
        return Response(response)


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
        tax_zip = request.POST.get('zip')
        price_calculator = PriceCalculator(coupon_code=None, email=None, tax_zip=tax_zip, effective_date=None)
        tax_rate = price_calculator.tax_rate
        return Response({
            'success': True,
            'tax_rate': float(tax_rate.total_rate) * 100,
            'detail': tax_rate.detail,
        })


class CheckScheduleConflictView(APIView):

    authentication_classes = (SessionAuthentication,)
    permission_classes = (HasReservationsAccess,)

    def post(self, request):
        try:
            out_at_date = datetime.datetime.strptime(request.POST.get('out_at_date'), '%m/%d/%Y').date()
            out_at_time = datetime.datetime.strptime(request.POST.get('out_at_time'), '%H:%M').time()
            out_at = datetime.datetime.combine(out_at_date, out_at_time)

            back_at_date = datetime.datetime.strptime(request.POST.get('back_at_date'), '%m/%d/%Y').date()
            back_at_time = datetime.datetime.strptime(request.POST.get('back_at_time'), '%H:%M').time()
            back_at = datetime.datetime.combine(back_at_date, back_at_time)
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
