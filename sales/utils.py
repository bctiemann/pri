import decimal
from abc import ABC

from django.conf import settings

from sales.models import Reservation, Coupon, TaxRate
from users.models import Customer


class PriceCalculator(ABC):
    """
    Abstract base class implementing utility methods for calculating price structure.
    Unimplemented methods must be implemented in subclasses such as RentalPriceCalculator.
    coupon_discount and customer_discount are common to all calculators; subclasses with other
    specific types of discounts should implement getter methods on a similar pattern.
    """

    tax_zip = None
    tax_rate = None

    coupon = None
    coupon_discount = None
    post_coupon_discount_subtotal = None

    customer = None
    customer_discount = None
    post_customer_discount_subtotal = None

    subtotal = 0.0
    cents = decimal.Decimal('0.01')

    def __init__(self, coupon_code=None, email=None, tax_zip=None):
        self.coupon = self.get_coupon(coupon_code)
        self.customer = self.get_customer(email)
        self.tax_rate = self.get_tax_rate(tax_zip)

    def get_coupon(self, coupon_code):
        return Coupon.objects.filter(code=coupon_code).first()

    def get_customer(self, email):
        return Customer.objects.filter(user__email=email).first()

    def get_tax_rate(self, tax_zip):
        tax_rate, tax_rate_created = TaxRate.objects.get_or_create(postal_code=tax_zip)
        return tax_rate

    def quantize_currency(self, value):
        # return f'{decimal.Decimal(value).quantize(self.cents, decimal.ROUND_HALF_UP)}'
        return decimal.Decimal(value).quantize(self.cents, decimal.ROUND_HALF_UP)

    def get_coupon_discount(self, value=None):
        if not self.coupon:
            return 0
        if value is None:
            raise ValueError('No base value provided.')
        return self.coupon.get_discount_value(value)

    def get_customer_discount(self, value=None):
        if value is None:
            raise ValueError('No base value provided.')
        if self.customer and self.customer.discount_pct:
            return value * self.customer.discount_pct / 100
        return 0

    def get_tax_amount(self, value=None):
        if value is None:
            value = self.pre_tax_subtotal
        return float(self.tax_rate.total_rate) * value

    def apply_discount(self, value=None):
        return self.subtotal - float(value)

    def apply_surcharge(self, value=None):
        return self.subtotal + float(value)

    @property
    def base_price(self):
        raise NotImplementedError

    @property
    def pre_tax_subtotal(self):
        # subtotal should be incrementally calculated in __init__() and returned as its final value
        return self.subtotal

    @property
    def total_with_tax(self):
        tax_amount = self.get_tax_amount(self.pre_tax_subtotal)
        return self.pre_tax_subtotal + tax_amount

    def get_price_data(self):
        raise NotImplementedError


class RentalPriceCalculator(PriceCalculator):
    """
    Price is calculated as follows:
    - Calculator is inited with vehicle, # days, extra miles, coupon code, email, and tax zip
    - Base price is daily rate * number of days
    - Subtract multi-day discount
    - Subtract coupon discount
    - Subtract customer ("promotional") discount
    - Add extra miles surcharge
    - Add sales tax

    Interim subtotals (e.g. post_multi_day_discount_subtotal) are for forensics and to return
    in price_data if necessary
    """
    vehicle_marketing = None

    num_days = None
    multi_day_discount = None
    post_multi_day_discount_subtotal = None

    extra_miles = None
    extra_miles_surcharge = None
    post_extra_miles_surcharge_subtotal = None

    def __init__(self, vehicle_marketing, num_days, extra_miles, **kwargs):
        super().__init__(**kwargs)
        self.vehicle_marketing = vehicle_marketing
        self.num_days = num_days
        self.extra_miles = int(extra_miles)

        self.subtotal = self.base_price

        # Multi-day discount
        self.multi_day_discount = self.get_multi_day_discount(value=self.subtotal)
        self.subtotal = self.apply_discount(value=self.multi_day_discount)
        self.post_multi_day_discount_subtotal = self.subtotal

        # Coupon discount
        self.coupon_discount = self.get_coupon_discount(value=self.subtotal)
        self.subtotal = self.apply_discount(value=self.coupon_discount)
        self.post_coupon_discount_subtotal = self.subtotal

        # Customer (promotional) discount
        self.customer_discount = self.get_customer_discount(value=self.subtotal)
        self.subtotal = self.apply_discount(value=self.customer_discount)
        self.post_customer_discount_subtotal = self.subtotal

        # Extra miles surcharge
        self.extra_miles_surcharge = self.get_extra_miles_cost()
        self.subtotal = self.apply_surcharge(value=self.extra_miles_surcharge)
        self.post_extra_miles_surcharge_subtotal = self.subtotal

    @property
    def base_price(self):
        return float(self.vehicle_marketing.price_per_day * self.num_days)

    @property
    def multi_day_discount_pct(self):
        if self.num_days >= 7:
            return self.vehicle_marketing.discount_7_day
        elif self.num_days >= 3:
            return self.vehicle_marketing.discount_3_day
        elif self.num_days >= 2:
            return self.vehicle_marketing.discount_2_day
        return 0

    def get_multi_day_discount(self, value=None):
        if not value:
            raise ValueError('No base value provided.')
        return value * self.multi_day_discount_pct / 100

    def get_extra_miles_cost(self):
        try:
            return settings.EXTRA_MILES_PRICES.get(self.extra_miles)['cost']
        except TypeError:
            return 0

    @property
    def reservation_deposit(self):
        return self.total_with_tax / 2

    def get_price_data(self):
        return dict(
            num_days=self.num_days,
            tax_rate=self.tax_rate.total_rate,
            customer_id=self.customer.id if self.customer else None,
            base_price=self.quantize_currency(self.base_price),
            multi_day_discount=self.quantize_currency(self.multi_day_discount),
            multi_day_discount_pct=self.multi_day_discount_pct,
            coupon_discount=self.quantize_currency(self.coupon_discount),
            customer_discount=self.quantize_currency(self.customer_discount),
            extra_miles=self.extra_miles,
            extra_miles_cost=self.quantize_currency(self.extra_miles_surcharge),
            subtotal=self.quantize_currency(self.pre_tax_subtotal),
            total_with_tax=self.quantize_currency(self.total_with_tax),
            reservation_deposit=self.quantize_currency(self.reservation_deposit),
            tax_amount=self.quantize_currency(self.get_tax_amount()),
        )


class PerformanceExperiencePriceCalculator(PriceCalculator):
    """
    Price is calculated as follows:
    - Calculator is inited with # drivers, # passengers, coupon code, email, and tax zip
    - Base price is per-driver rate * number of drivers, + per-passenger rate * number of passengers
    - Subtract coupon discount
    - Subtract customer ("promotional") discount
    - Add sales tax
    """
    num_drivers = None
    num_passengers = None

    def __init__(self, num_drivers, num_passengers, **kwargs):
        self.num_drivers = num_drivers
        self.num_passengers = num_passengers
        super().__init__(**kwargs)
