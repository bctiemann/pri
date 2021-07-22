import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import APIException

from django.urls import reverse_lazy, reverse
from django.db import IntegrityError
from django.contrib.auth import authenticate, login

from sales.forms import ReservationRentalDetailsForm, ReservationRentalPaymentForm
from sales.models import Reservation, generate_code
from sales.enums import ReservationType
from users.models import User, Customer, generate_password

logger = logging.getLogger(__name__)


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

    def post(self, request):
        # form = ReservationRentalDetailsForm(request.POST)
        form = ReservationRentalPaymentForm(request.POST)
        print(form.data)
        print(form.is_valid())
        print(form.errors.as_json())
        if not form.is_valid():
            return Response({
                'success': False,
                'errors': form.errors,
            })

        # Create Customer or login existing user
        if form.customer:
            if authenticate(request, username=form.customer.user.email, password=form.cleaned_data['password']):
                login(request, form.customer.user)
            else:
                return Response({
                    'success': False,
                    'errors': {
                        'password': ['Incorrect password'],
                    },
                })
            customer = form.customer
        else:
            # Create Customer object and login
            user = User.objects.create_user(form.cleaned_data['email'], password=generate_password())
            customer_kwargs = {key: form.cleaned_data.get(key) for key in form.customer_fields}
            customer = Customer.objects.create(
                user=user,
                **customer_kwargs,
            )
            login(request, user)

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
