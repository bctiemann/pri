from rest_framework.views import APIView
from rest_framework.response import Response

from sales.forms import ReservationRentalDetailsForm


class ValidateRentalDetailsView(APIView):

    def post(self, request):
        form = ReservationRentalDetailsForm(request.POST)
        print(form.data)
        print(form.is_valid())
        print(form.errors.as_json())
        response = {
            'success': form.is_valid(),
            'errors': form.errors,
        }
        return Response(response)
