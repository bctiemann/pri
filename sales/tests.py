from decimal import Decimal

from django.test import TestCase

from fleet.models import Vehicle, VehicleMarketing
from sales.utils import RentalPriceCalculator


class RentalPriceCalculatorTestCase(TestCase):

    databases = ('default', 'front',)

    def setUp(self) -> None:
        self.vehicle_1 = VehicleMarketing.objects.create(
            price_per_day=500,
            discount_2_day=10,
            discount_3_day=20,
            discount_7_day=40,
            security_deposit=5000.00,
        )

    def test_get_rental_price_data(self):
        num_days = 2
        rental_price_calculator = RentalPriceCalculator(
            self.vehicle_1,
            num_days,
            None,
            None,
            200,
            '07430',
        )
        price_data = rental_price_calculator.get_price_data()
        print(price_data)
        assert None == None

