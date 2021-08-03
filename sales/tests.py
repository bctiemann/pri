from decimal import Decimal

from django.test import TestCase

from fleet.models import VehicleMarketing
from users.models import Customer
from sales.models import TaxRate, Coupon
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
        self.tax_rate_1 = TaxRate.objects.create(
            postal_code='07430',
            total_rate=0.06625,
        )
        self.customer_1 = Customer.objects.create(
            discount_pct=10,
        )
        self.coupon_1 = Coupon.objects.create(
            amount=15.00,
        )

    def test_get_rental_price_data(self):
        vehicle_marketing = self.vehicle_1
        num_days = 2
        coupon_code = None
        email = None
        extra_miles = 200
        tax_zip = '07430'
        rental_price_calculator = RentalPriceCalculator(
            vehicle_marketing, num_days, coupon_code, email, extra_miles, tax_zip,
        )
        price_data = rental_price_calculator.get_price_data()
        print(price_data)

        self.assertEqual(price_data['total_with_tax'], Decimal('1215.53'))

