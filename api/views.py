import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import APIException

from django.urls import reverse_lazy, reverse
from django.db import IntegrityError

from sales.forms import ReservationRentalDetailsForm, ReservationRentalPaymentForm
from sales.models import Reservation, generate_code
from sales.enums import ReservationType

logger = logging.getLogger(__name__)


class ValidateRentalDetailsView(APIView):

    def post(self, request):
        form = ReservationRentalDetailsForm(request.POST)
        print(form.data)
        print(form.is_valid())
        print(form.errors.as_json())
        response = {
            'success': form.is_valid(),
            'errors': form.errors,
            'errors_html': form.errors.as_ul(),
            'price_data': form.price_data,
            'delivery_required': form.cleaned_data['delivery_required'],
        }
        return Response(response)


class ValidateRentalPaymentView(APIView):

    def post(self, request):
        form = ReservationRentalDetailsForm(request.POST)
        payment_form = ReservationRentalPaymentForm(request.POST)
        print(form.data)
        print(form.is_valid())
        print(form.errors.as_json())

        # Create Customer or login existing user

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

                )
            except IntegrityError:
                logger.warning(f'Confirmation code collision: {confirmation_code}')
                retries_left -= 1
        if not reservation:
            raise APIException(detail='Failed to generate a unique confirmation code.', code='collision')

        response = {
            'success': form.is_valid() and payment_form.is_valid(),
            'errors': form.errors,
            'errors_html': form.errors.as_ul(),
            'reservation_type': 'rental',
            'customer_site_url': reverse('customer_portal:confirm-reservation', kwargs={'confirmation_code': confirmation_code}),
        }
        return Response(response)
