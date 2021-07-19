from sales.models import Reservation, Coupon, TaxRate
from users.models import Customer


class PriceCalculator:
    vehicle_marketing = None
    coupon = None
    customer = None

    rental_duration = None
    num_days = None
    sales_tax = None
    customer_id = None
    num_drivers = None
    total_cost_raw = None
    total_cost = None
    coupon_discount = None
    customer_discount = None
    customer_discount_pct = None
    multi_day_discount = None
    multi_day_discount_pct = None
    extra_miles = None
    extra_miles_cost = None
    subtotal = None
    total_with_tax = 0
    reservation_deposit = None
    tax_amount = None
    delivery = None
    deposit = None

    def __init__(self, vehicle_marketing, num_days, coupon_code=None, email=None, extra_miles=None, tax_zip=None):
        self.vehicle_marketing = vehicle_marketing
        self.num_days = num_days
        self.extra_miles = extra_miles
        self.tax_zip = tax_zip

        try:
            self.coupon = Coupon.objects.get(code=coupon_code)
        except Coupon.DoesNotExist:
            pass

        try:
            self.customer = Customer.objects.get(user__email=email)
        except Customer.DoesNotExist:
            pass

        self.tax_rate, tax_rate_created = TaxRate.objects.get_or_create(postal_code=tax_zip)

    def get_coupon_discount(self, value):
        if not self.coupon:
            return 0
        return self.coupon.get_discount_value(value)

    def get_customer_discount(self, value):
        print(self.customer)
        if self.customer:
            return value * self.customer.discount_pct / 100
        return 0

    def get_tax_amount(self, value):
        return self.tax_rate.total_rate * value

    @property
    def raw_cost(self):
        return self.vehicle_marketing.price_per_day * self.num_days

    def get_price_data(self):
        raw_cost = self.raw_cost
        subtotal = raw_cost

        # Multi-day discount

        # Coupon discount
        coupon_discount = self.get_coupon_discount(subtotal)
        subtotal -= coupon_discount
        print(subtotal)

        # Customer discount
        customer_discount = self.get_customer_discount(subtotal)
        subtotal -= customer_discount
        print(subtotal)

        # Extra miles

        # Sales tax

        return dict(
            rental_duration=self.rental_duration,
            num_days=self.num_days,
            tax_rate=self.tax_rate.total_rate,
            customer_id=None,
            num_drivers=None,
            total_cost_raw=self.raw_cost,
            total_cost=None,
            coupon_discount=self.get_coupon_discount(self.raw_cost),
            customer_discount=self.get_customer_discount(self.raw_cost),
            customer_discount_pct=None,
            multi_day_discount=0,
            multi_day_discount_pct=None,
            extra_miles=None,
            extra_miles_cost=0,
            subtotal=subtotal,
            total_with_tax=self.total_with_tax,
            reservation_deposit=0,
            tax_amount=self.get_tax_amount(subtotal),
            delivery=None,
            deposit=0,
        )
