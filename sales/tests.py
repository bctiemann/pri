from decimal import Decimal
from datetime import date

from django.test import TestCase

from fleet.models import VehicleMarketing
from users.models import Customer, User
from sales.models import TaxRate, Coupon, Promotion
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
        self.user_1 = User.objects.create_user(
            email='email@test.com',
        )
        self.customer_1 = Customer.objects.create(
            user=self.user_1,
            discount_pct=10,
        )
        self.coupon_1 = Coupon.objects.create(
            amount=15.00,
            code='TEST',
        )
        self.coupon_2 = Coupon.objects.create(
            amount=15.00,
            code='EXPIRED',
            end_date=date(2021, 12, 31),
        )
        self.promotion_1 = Promotion.objects.create(
            percent=20,
            name='Father\'s Day',
            end_date=date(2022, 6, 11),
        )

    def test_get_tax_rate_from_avalara_api(self):
        """
        Make live query to Avalara API and check that a valid response is returned
        """
        tax_rate = TaxRate.objects.create(
            postal_code='34210'
        )
        assert tax_rate.total_rate == 0.07

    def test_get_rental_price_data(self):
        """
        2-day rental, 200 extra miles, no coupon, no customer discount
        """
        vehicle_marketing = self.vehicle_1
        num_days = 2
        coupon_code = None
        email = None
        extra_miles = 200
        tax_zip = '07430'
        effective_date = None
        rental_price_calculator = RentalPriceCalculator(
            vehicle_marketing, num_days, extra_miles, coupon_code=coupon_code, email=email, tax_zip=tax_zip, effective_date=effective_date
        )
        price_data = rental_price_calculator.get_price_data()

        self.assertEqual(price_data['extra_miles_cost'], Decimal('330.00'))
        self.assertEqual(price_data['total_with_tax'], Decimal('1311.49'))

    def test_get_rental_price_data_with_coupon(self):
        """
        2-day rental, 200 extra miles, $15 coupon, no customer discount
        """
        vehicle_marketing = self.vehicle_1
        num_days = 2
        coupon_code = 'TEST'
        email = None
        extra_miles = 200
        tax_zip = '07430'
        effective_date = date(2022, 6, 12)
        rental_price_calculator = RentalPriceCalculator(
            vehicle_marketing, num_days, extra_miles, coupon_code=coupon_code, email=email, tax_zip=tax_zip, effective_date=effective_date
        )
        price_data = rental_price_calculator.get_price_data()

        self.assertEqual(price_data['coupon_discount'], Decimal('15.00'))
        self.assertEqual(price_data['total_with_tax'], Decimal('1295.49'))

    def test_get_rental_price_data_with_expired_coupon(self):
        """
        2-day rental, 200 extra miles, $15 coupon (expired), no customer discount
        """
        vehicle_marketing = self.vehicle_1
        num_days = 2
        coupon_code = 'EXPIRED'
        email = None
        extra_miles = 200
        tax_zip = '07430'
        effective_date = date(2022, 6, 12)
        rental_price_calculator = RentalPriceCalculator(
            vehicle_marketing, num_days, extra_miles, coupon_code=coupon_code, email=email, tax_zip=tax_zip, effective_date=effective_date
        )
        price_data = rental_price_calculator.get_price_data()

        self.assertEqual(price_data['coupon_discount'], Decimal('0.00'))
        self.assertEqual(price_data['total_with_tax'], Decimal('1311.49'))

    def test_get_rental_price_data_with_customer_discount(self):
        """
        2-day rental, 200 extra miles, no coupon, 10% customer discount
        """
        vehicle_marketing = self.vehicle_1
        num_days = 2
        coupon_code = None
        email = 'email@test.com'
        extra_miles = 200
        tax_zip = '07430'
        effective_date = None
        rental_price_calculator = RentalPriceCalculator(
            vehicle_marketing, num_days, extra_miles, coupon_code=coupon_code, email=email, tax_zip=tax_zip, effective_date=effective_date
        )
        price_data = rental_price_calculator.get_price_data()

        self.assertEqual(price_data['customer_id'], 1)
        self.assertEqual(price_data['customer_discount'], Decimal('90.00'))
        self.assertEqual(price_data['total_with_tax'], Decimal('1215.53'))

    def test_get_rental_price_data_with_promotional_discount(self):
        """
        2-day rental, 200 extra miles, no coupon, 20% promotional discount
        """
        vehicle_marketing = self.vehicle_1
        num_days = 2
        coupon_code = None
        email = None
        extra_miles = 200
        tax_zip = '07430'
        effective_date = date(2022, 6, 10)
        rental_price_calculator = RentalPriceCalculator(
            vehicle_marketing, num_days, extra_miles, coupon_code=coupon_code, email=email, tax_zip=tax_zip, effective_date=effective_date
        )
        price_data = rental_price_calculator.get_price_data()

        self.assertEqual(price_data['promotion_discount'], Decimal('180.00'))
        self.assertEqual(price_data['total_with_tax'], Decimal('1119.56'))

    def test_get_rental_price_data_with_military_discount(self):
        """
        2-day rental, 200 extra miles, no coupon, no promotional discount, 10% military discount
        """
        vehicle_marketing = self.vehicle_1
        num_days = 2
        coupon_code = None
        email = None
        extra_miles = 200
        tax_zip = '07430'
        effective_date = None
        rental_price_calculator = RentalPriceCalculator(
            vehicle_marketing,
            num_days,
            extra_miles,
            coupon_code=coupon_code,
            email=email,
            tax_zip=tax_zip,
            effective_date=effective_date,
            is_military=True,
        )
        price_data = rental_price_calculator.get_price_data()

        self.assertEqual(price_data['military_discount'], Decimal('90.00'))
        self.assertEqual(price_data['total_with_tax'], Decimal('1215.53'))

