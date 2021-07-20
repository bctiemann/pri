from rest_framework.views import APIView
from rest_framework.response import Response

from sales.forms import ReservationRentalDetailsForm, ReservationRentalPaymentForm


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

        response = {
            'success': form.is_valid() and payment_form.is_valid(),
            'errors': form.errors,
            'errors_html': form.errors.as_ul(),
            'reservation_type': 'rental',
        }
        return Response(response)
