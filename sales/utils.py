from django.conf import settings

from sales.models import Reservation, Coupon, TaxRate
from users.models import Customer


class PriceCalculator:

    # rental_duration = None
    # sales_tax = None
    # customer_id = None
    # num_drivers = None
    # total_cost_raw = None
    # total_cost = None
    # coupon_discount = None
    # customer_discount = None
    # customer_discount_pct = None
    # multi_day_discount = None
    # multi_day_discount_pct = None
    # extra_miles_cost = None
    # subtotal = None
    # total_with_tax = 0
    # reservation_deposit = None
    # tax_amount = None
    # delivery = None
    # deposit = None
    
    pass


class RentalPriceCalculator(PriceCalculator):
    """
    Price is calculated as follows:
    - Base price is daily rate * number of days
    - Subtract multi-day discount
    - Subtract coupon discount
    - Subtract customer ("promotional") discount
    - Add extra miles cost
    - Add sales tax
    """
    vehicle_marketing = None
    num_days = None
    extra_miles = None
    tax_zip = None
    tax_rate = None
    coupon = None
    customer = None

    def __init__(self, vehicle_marketing, num_days, coupon_code=None, email=None, extra_miles=None, tax_zip=None):
        self.vehicle_marketing = vehicle_marketing
        self.num_days = num_days
        self.extra_miles = int(extra_miles)
        self.tax_zip = tax_zip
        self.tax_rate, tax_rate_created = TaxRate.objects.get_or_create(postal_code=tax_zip)

        try:
            self.coupon = Coupon.objects.get(code=coupon_code)
        except Coupon.DoesNotExist:
            pass

        try:
            self.customer = Customer.objects.get(user__email=email)
        except Customer.DoesNotExist:
            pass

    @property
    def multi_day_discount_pct(self):
        if self.num_days >= 7:
            return self.vehicle_marketing.discount_7_day
        elif self.num_days >= 3:
            return self.vehicle_marketing.discount_3_day
        elif self.num_days >= 2:
            return self.vehicle_marketing.discount_2_day
        return 0

    def get_multi_day_discount(self, value):
        return value * self.multi_day_discount_pct / 100

    def get_coupon_discount(self, value):
        if not self.coupon:
            return 0
        return self.coupon.get_discount_value(value)

    def get_customer_discount(self, value):
        if self.customer and self.customer.discount_pct:
            return value * self.customer.discount_pct / 100
        return 0

    def get_tax_amount(self, value):
        return self.tax_rate.total_rate * value

    @property
    def base_price(self):
        return self.vehicle_marketing.price_per_day * self.num_days

    @property
    def post_multi_day_discount_subtotal(self):
        subtotal = self.base_price
        multi_day_discount = self.get_multi_day_discount(subtotal)
        subtotal -= multi_day_discount
        return subtotal

    @property
    def post_coupon_discount_subtotal(self):
        subtotal = self.post_multi_day_discount_subtotal
        coupon_discount = self.get_coupon_discount(subtotal)
        subtotal -= coupon_discount
        return subtotal

    @property
    def post_customer_discount_subtotal(self):
        subtotal = self.post_coupon_discount_subtotal
        customer_discount = self.get_customer_discount(subtotal)
        subtotal -= customer_discount
        return subtotal

    @property
    def extra_miles_cost(self):
        try:
            return settings.EXTRA_MILES_PRICES.get(self.extra_miles)['cost']
        except TypeError:
            return 0

    @property
    def pre_tax_subtotal(self):
        subtotal = self.post_customer_discount_subtotal
        subtotal += self.extra_miles_cost
        return subtotal

    @property
    def total_with_tax(self):
        tax_amount = self.get_tax_amount(self.pre_tax_subtotal)
        return self.pre_tax_subtotal + tax_amount

    @property
    def reservation_deposit(self):
        return self.total_with_tax / 2

    def get_price_data(self):
        return dict(
            num_days=self.num_days,
            tax_rate=self.tax_rate.total_rate,
            customer_id=self.customer.id if self.customer else None,
            base_price=self.base_price,
            multi_day_discount=self.get_multi_day_discount(self.base_price),
            multi_day_discount_pct=self.multi_day_discount_pct,
            coupon_discount=self.get_coupon_discount(self.post_multi_day_discount_subtotal),
            customer_discount=self.get_customer_discount(self.post_coupon_discount_subtotal),
            extra_miles=self.extra_miles,
            extra_miles_cost=self.extra_miles_cost,
            subtotal=self.pre_tax_subtotal,
            total_with_tax=self.total_with_tax,
            reservation_deposit=self.reservation_deposit,
            tax_amount=self.get_tax_amount(self.pre_tax_subtotal),
        )
