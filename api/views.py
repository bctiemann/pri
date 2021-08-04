import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import APIException

from django.urls import reverse_lazy, reverse
from django.db import IntegrityError
from django.contrib.auth import authenticate, login
from django.http import Http404, HttpResponseRedirect

from sales.forms import ReservationRentalDetailsForm, ReservationRentalPaymentForm, ReservationRentalLoginForm
from sales.models import Reservation, generate_code
from sales.enums import ReservationType
from users.models import User, Customer, generate_password
from fleet.models import Vehicle, VehicleMarketing, VehiclePicture
from api.serializers import VehicleSerializer

logger = logging.getLogger(__name__)


class GetVehiclesView(APIView):

    def get(self, request):
        vehicles = VehicleMarketing.objects.all()
        serializer = VehicleSerializer(vehicles, many=True)
        return Response(serializer.data)


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
            if authenticate(request, username=form.customer.user.email, password=form.cleaned_data['password']):
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


# Single entrypoint to handle all API calls from mobile app
class LegacyPostView(APIView):

    def post(self, request):
        method = request.POST.get('method')

        if method == 'getVehicles':
            view = GetVehiclesView()
            return view.get(request)

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
