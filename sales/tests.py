from decimal import Decimal
from datetime import date
from freezegun import freeze_time

from django.test import TestCase
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from fleet.models import Vehicle, VehicleMarketing, VehicleStatus
from users.models import Customer, User
from sales.models import TaxRate, Coupon, Promotion
from sales.calculators import RentalPriceCalculator


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
        self.assertEqual(price_data['specific_discount_label'], 'Coupon discount')
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
        self.assertEqual(price_data['specific_discount'], Decimal('0.00'))
        self.assertEqual(price_data['specific_discount_label'], '')
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
        self.assertEqual(price_data['specific_discount_label'], 'Customer discount')
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
        self.assertEqual(price_data['specific_discount_label'], 'Promotional discount')
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
        self.assertEqual(price_data['specific_discount_label'], 'Military discount')
        self.assertEqual(price_data['total_with_tax'], Decimal('1215.53'))

    def test_get_rental_price_data_with_one_time_discount(self):
        """
        2-day rental, 200 extra miles, no coupon, no promotional discount, 20% one-time discount
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
            is_military=False,
            one_time_discount_pct=20,
        )
        price_data = rental_price_calculator.get_price_data()

        self.assertEqual(price_data['one_time_discount'], Decimal('180.00'))
        self.assertEqual(price_data['specific_discount_label'], 'One-time discount')
        self.assertEqual(price_data['total_with_tax'], Decimal('1119.56'))


    def test_get_rental_price_data_with_override_subtotal(self):
        """
        2-day rental, 200 extra miles, discounts, subtotal overridden to 1400.00
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
            override_subtotal=1400.00,
        )
        price_data = rental_price_calculator.get_price_data()

        self.assertEqual(price_data['computed_subtotal'], Decimal('1140.00'))
        self.assertEqual(price_data['subtotal'], Decimal('1400.00'))
        self.assertEqual(price_data['total_with_tax'], Decimal('1492.75'))


class RentalTestCase(TestCase):

    databases = ('default', 'front',)

    def setUp(self) -> None:
        self.client = Client()
        self.vehiclemarketing_1 = VehicleMarketing.objects.create(
            id=1,
            slug='test-vehicle',
            status=VehicleStatus.READY,
            price_per_day=500,
            discount_2_day=10,
            discount_3_day=20,
            discount_7_day=40,
            security_deposit=5000.00,
        )
        self.vehicle_1 = Vehicle.objects.create(vehicle_marketing_id=self.vehiclemarketing_1.id)

    def test_empty_post(self):
        url = reverse('validate-rental-details')
        post_data = dict()
        response = self.client.post(url, post_data)
        result = response.json()
        self.assertFalse(result['success'])
        errors = result['errors']
        self.assertIn('vehicle_marketing', errors)
        self.assertIn('out_at', errors)
        self.assertIn('back_at', errors)
        self.assertIn('out_date', errors)
        self.assertIn('back_date', errors)
        self.assertIn('email', errors)
        self.assertIn('drivers', errors)
        self.assertEqual(list(errors.keys())[0], 'out_at')

    def test_defaults(self):
        url = reverse('validate-rental-details')
        post_data = dict(
            vehicle_marketing=1,
            vehicle_slug='test-vehicle',
            out_date='',
            out_time='07:00',
            back_date='',
            back_time='07:00',
            drivers='1',
            delivery_required='0',
            delivery_zip='',
            extra_miles='0',
            email='',
            coupon_code='',
            is_military=False,
            customer_notes='',
        )
        response = self.client.post(url, post_data)
        result = response.json()
        self.assertFalse(result['success'])
        errors = result['errors']
        self.assertIn('out_at', errors)
        self.assertIn('back_at', errors)
        self.assertIn('out_date', errors)
        self.assertIn('back_date', errors)
        self.assertIn('email', errors)

    @freeze_time('2023-02-01 15:00:00')
    def test_valid_rental_single_day(self):
        url = reverse('validate-rental-details')
        post_data = dict(
            vehicle_marketing=1,
            vehicle_slug='test-vehicle',
            out_date='04/25/2023',
            out_time='17:00',
            back_date='04/26/2023',
            back_time='17:00',
            drivers='1',
            delivery_required='0',
            delivery_zip='',
            extra_miles='0',
            email='test@test.com',
            coupon_code='',
            is_military=False,
            customer_notes='',
        )
        response = self.client.post(url, post_data)
        result = response.json()
        self.assertTrue(result['success'])
        self.assertEqual(result['errors'], {})
        self.assertIsNone(result['customer_id'])
        self.assertEqual(result['price_data']['total_with_tax'], Decimal(533.13))
        self.assertEqual(result['price_data']['tax_amount'], Decimal(33.13))
        self.assertEqual(result['price_data']['reservation_deposit'], Decimal(266.56))
        self.assertEqual(result['price_data']['multi_day_discount'], Decimal(0.0))
        self.assertEqual(result['price_data']['specific_discount'], Decimal(0.0))
        self.assertEqual(result['price_data']['specific_discount_label'], '')

    @freeze_time('2023-02-01 15:00:00')
    def test_invalid_rental_negative_duration(self):
        url = reverse('validate-rental-details')
        post_data = dict(
            vehicle_marketing=1,
            vehicle_slug='test-vehicle',
            out_date='04/25/2023',
            out_time='17:00',
            back_date='04/24/2023',
            back_time='17:00',
        )
        response = self.client.post(url, post_data)
        result = response.json()
        self.assertFalse(result['success'])
        self.assertEqual(result['errors']['back_at'], ["You've specified a return date earlier than the rental date."])
        self.assertEqual(result['errors']['back_date'], result['errors']['back_at'])

    @freeze_time('2023-02-01 15:00:00')
    def test_invalid_rental_date_in_past(self):
        url = reverse('validate-rental-details')
        post_data = dict(
            vehicle_marketing=1,
            vehicle_slug='test-vehicle',
            out_date='01/25/2023',
            out_time='17:00',
            back_date='01/26/2023',
            back_time='17:00',
        )
        response = self.client.post(url, post_data)
        result = response.json()
        self.assertFalse(result['success'])
        self.assertEqual(result['errors']['back_at'], ["You've specified a rental date in the past."])
        self.assertEqual(result['errors']['back_date'], result['errors']['back_at'])

    @freeze_time('2023-02-01 15:00:00')
    def test_invalid_vehicle(self):
        url = reverse('validate-rental-details')
        post_data = dict(
            vehicle_marketing=2,
            vehicle_slug='test-vehicle-2',
            out_date='02/25/2023',
            out_time='17:00',
            back_date='02/26/2023',
            back_time='17:00',
        )
        response = self.client.post(url, post_data)
        result = response.json()
        self.assertFalse(result['success'])
        self.assertEqual(result['errors']['vehicle_marketing'], ['Select a valid choice. That choice is not one of the available choices.'])
        self.assertIn('Invalid vehicle specified.', result['errors']['__all__'])
