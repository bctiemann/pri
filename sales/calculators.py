import datetime
import decimal
from abc import ABC
from typing import Optional

from django.conf import settings
from django.db.models import Q

from fleet.models import VehicleMarketing
from sales.models import Promotion, Coupon, TaxRate
from sales.enums import ServiceType
from users.models import Customer


def quantize_currency(value) -> decimal.Decimal:
    cents = decimal.Decimal('0.01')
    return decimal.Decimal(value).quantize(cents, decimal.ROUND_HALF_UP)


class PriceCalculator(ABC):
    """
    Abstract base class implementing utility methods for calculating price structure.
    Unimplemented methods must be implemented in subclasses such as RentalPriceCalculator.
    Promotion/coupon/customer/military/one-time discounts are common to all calculators; subclasses
    with other specific types of discounts (such as multi-day) should implement getter methods on
    a similar pattern.
    """
    service_type: ServiceType = None

    tax_zip: str = None
    tax_rate: TaxRate = None
    effective_date: datetime.date = None

    promotion: Promotion = None
    promotion_discount: float = None
    post_promotion_discount_subtotal: float = None

    coupon: Coupon = None
    coupon_discount: float = None
    post_coupon_discount_subtotal: float = None

    customer: Customer = None
    customer_discount: float = None
    post_customer_discount_subtotal: float = None

    is_military: bool = False
    military_discount: float = None
    post_military_discount_subtotal: float = None

    one_time_discount: float = None
    one_time_discount_pct: float = None
    post_one_time_discount_subtotal: float = None

    specific_discount: float = None
    specific_discount_label: str = ''
    post_specific_discount: float = None

    subtotal: float = 0.0
    override_subtotal: float = None

    def __init__(
            self,
            coupon_code: str,
            email: str,
            tax_zip: str,
            effective_date: datetime.date = None,
            is_military: bool = False,
            override_subtotal: float = None,
            one_time_discount_pct: float = None,
    ):
        self.effective_date = effective_date
        self.promotion = self.get_effective_promotion()
        self.coupon = self.get_coupon(coupon_code)
        self.customer = self.get_customer(email)
        self.tax_rate = self.get_tax_rate(tax_zip)
        self.tax_zip = tax_zip
        self.is_military = is_military
        if override_subtotal:
            self.override_subtotal = float(override_subtotal)
        self.one_time_discount_pct = one_time_discount_pct

    def get_effective_promotion(self) -> Optional[Promotion]:
        if not self.effective_date:
            return None
        # Get all promotions in effect on the given date
        effective_promotions = Promotion.objects.filter(
            (Q(start_date__isnull=True) | Q(start_date__lte=self.effective_date)),
            end_date__gte=self.effective_date,
        )
        # Restrict to a specific service type if given
        if self.service_type:
            effective_promotions = effective_promotions.filter(
                Q(service_type='') | Q(service_type=self.service_type.value)
            )
        return effective_promotions.first()

    def get_coupon(self, coupon_code: str) -> Optional[Coupon]:
        return Coupon.objects.filter(code__iexact=coupon_code).first()

    def get_customer(self, email: str) -> Optional[Customer]:
        return Customer.objects.filter(user__email=email).first()

    def get_tax_rate(self, tax_zip: str) -> TaxRate:
        if not tax_zip:
            raise ValueError('No tax ZIP provided.')
        tax_rate, tax_rate_created = TaxRate.objects.get_or_create(postal_code=tax_zip)
        return tax_rate

    def get_promotion_discount(self, value: float = None) -> float:
        if not self.promotion:
            return 0
        if value is None:
            raise ValueError('No base value provided.')
        return self.promotion.get_discount_value(value)

    def get_coupon_discount(self, value=None) -> float:
        if not self.coupon:
            return 0
        if value is None:
            raise ValueError('No base value provided.')
        if self.coupon.is_expired_on(self.effective_date):
            return 0
        return self.coupon.get_discount_value(value)

    def get_customer_discount(self, value=None) -> float:
        if value is None:
            raise ValueError('No base value provided.')
        if self.customer and self.customer.discount_pct:
            return value * self.customer.discount_pct / 100
        return 0

    def get_military_discount(self, value=None) -> float:
        if value is None:
            raise ValueError('No base value provided.')
        if self.is_military:
            return value * settings.MILITARY_DISCOUNT_PCT / 100
        return 0

    def get_one_time_discount(self, value: float = None) -> float:
        if value is None:
            raise ValueError('No base value provided.')
        if self.one_time_discount_pct:
            return value * self.one_time_discount_pct / 100
        return 0

    def calculate_specific_discount(self, value: float) -> None:
        self.promotion_discount = self.get_promotion_discount(value=value)
        self.coupon_discount = self.get_coupon_discount(value=value)
        self.customer_discount = self.get_customer_discount(value=value)
        self.military_discount = self.get_military_discount(value=value)
        self.one_time_discount = self.get_one_time_discount(value=value)

        specific_discounts = [
            dict(discount=self.promotion_discount, label='Promotional discount'),
            dict(discount=self.coupon_discount, label='Coupon discount'),
            dict(discount=self.customer_discount, label='Customer discount'),
            dict(discount=self.military_discount, label='Military discount'),
            dict(discount=self.one_time_discount, label='One-time discount'),
        ]

        specific_discounts = sorted(specific_discounts, key=lambda x: x['discount'], reverse=True)
        self.specific_discount = specific_discounts[0]['discount']
        if self.specific_discount:
            self.specific_discount_label = specific_discounts[0]['label']

    def get_tax_amount(self, value: float = None) -> float:
        if value is None:
            value = self.pre_tax_subtotal
        return float(self.tax_rate.total_rate) * value

    def apply_discount(self, value: float = None) -> float:
        return self.subtotal - float(value)

    def apply_surcharge(self, value: float = None) -> float:
        return self.subtotal + float(value)

    @property
    def base_price(self) -> float:
        raise NotImplementedError

    @property
    def computed_subtotal(self) -> float:
        return self.subtotal

    @property
    def pre_tax_subtotal(self) -> float:
        # subtotal should be incrementally calculated in __init__() and returned as its final value
        return self.override_subtotal or self.computed_subtotal

    @property
    def total_with_tax(self) -> float:
        tax_amount = self.get_tax_amount(self.pre_tax_subtotal)
        return self.pre_tax_subtotal + tax_amount

    def get_price_data(self) -> dict:
        raise NotImplementedError


class RentalPriceCalculator(PriceCalculator):
    """
    Price is calculated as follows:
    - Calculator is inited with:
        - vehicle
        - # days
        - extra miles
        - coupon code
        - email
        - tax zip
        - effective date
        - military status
        - Subtotal override
        - one-time discount
    - Base price is daily rate * number of days
    - Subtract multi-day discount
    - Subtract largest of (coupon discount, customer discount, promotional discount, military discount, one-time discount)
    - Add extra miles surcharge
    - If subtotal override is provided, it takes the place of the subtotal here
    - Add sales tax

    Interim subtotals (e.g. post_multi_day_discount_subtotal) are for forensics and to return
    in price_data if necessary
    """
    service_type = ServiceType.RENTAL

    vehicle_marketing: VehicleMarketing = None

    num_days: int = None
    multi_day_discount: float = None
    post_multi_day_discount_subtotal: float = None

    specific_discount: float = None
    post_specific_discount_subtotal: float = None

    extra_miles: int = None
    extra_miles_surcharge: float = None
    post_extra_miles_surcharge_subtotal: float = None

    def __init__(self, vehicle_marketing: VehicleMarketing, num_days: int, extra_miles: int, **kwargs):
        # Initialize objects handled by superclass
        super().__init__(**kwargs)

        # initialize objects specific to this calculator class
        self.vehicle_marketing = vehicle_marketing
        self.num_days = num_days
        self.extra_miles = int(extra_miles)

        # Start by calculating the base price
        self.subtotal = self.base_price

        # Multi-day discount
        self.multi_day_discount = self.get_multi_day_discount(value=self.subtotal)
        self.subtotal = self.apply_discount(value=self.multi_day_discount)
        self.post_multi_day_discount_subtotal = self.subtotal

        # Find and apply greatest specific discount available
        self.calculate_specific_discount(value=self.subtotal)
        self.subtotal = self.apply_discount(value=self.specific_discount)
        self.post_specific_discount_subtotal = self.subtotal

        # Extra miles surcharge
        self.extra_miles_surcharge = self.get_extra_miles_cost()
        self.subtotal = self.apply_surcharge(value=self.extra_miles_surcharge)
        self.post_extra_miles_surcharge_subtotal = self.subtotal

        # Superclass handles sales tax and total from here

    @property
    def base_price(self) -> float:
        return float(self.vehicle_marketing.price_per_day * self.num_days)

    @property
    def multi_day_discount_pct(self) -> int:
        if self.num_days >= 7:
            return self.vehicle_marketing.discount_7_day
        elif self.num_days >= 3:
            return self.vehicle_marketing.discount_3_day
        elif self.num_days >= 2:
            return self.vehicle_marketing.discount_2_day
        return 0

    def get_multi_day_discount(self, value: float = None) -> float:
        if value is None:
            raise ValueError('No base value provided.')
        return value * self.multi_day_discount_pct / 100

    def get_extra_miles_cost(self) -> float:
        try:
            return settings.EXTRA_MILES_PRICES.get(self.extra_miles)['cost']
        except TypeError:
            return 0

    @property
    def reservation_deposit(self) -> float:
        return self.total_with_tax / 2

    def get_price_data(self) -> dict:
        return dict(
            vehicle_price_per_day=quantize_currency(self.vehicle_marketing.price_per_day),
            num_days=self.num_days,
            tax_zip=self.tax_zip,
            tax_rate=self.tax_rate.total_rate,
            tax_rate_as_percent=self.tax_rate.total_rate * 100,
            customer_id=self.customer.id if self.customer else None,
            base_price=quantize_currency(self.base_price),
            multi_day_discount=quantize_currency(self.multi_day_discount),
            multi_day_discount_pct=self.multi_day_discount_pct,
            post_multi_day_discount_subtotal=quantize_currency(self.post_multi_day_discount_subtotal),
            promotion_discount=quantize_currency(self.promotion_discount),
            coupon_discount=quantize_currency(self.coupon_discount),
            customer_discount=quantize_currency(self.customer_discount),
            military_discount=quantize_currency(self.military_discount),
            one_time_discount=quantize_currency(self.one_time_discount),
            specific_discount=quantize_currency(self.specific_discount),
            specific_discount_label=self.specific_discount_label,
            extra_miles=self.extra_miles,
            extra_miles_cost=quantize_currency(self.extra_miles_surcharge),
            subtotal=quantize_currency(self.pre_tax_subtotal),
            computed_subtotal=quantize_currency(self.computed_subtotal),
            total_with_tax=quantize_currency(self.total_with_tax),
            reservation_deposit=quantize_currency(self.reservation_deposit),
            tax_amount=quantize_currency(self.get_tax_amount()),
        )


class PerformanceExperiencePriceCalculator(PriceCalculator):
    """
    Price is calculated as follows:
    - Calculator is inited with # drivers, # passengers, coupon code, email, and tax zip
    - Base price is predefined per number of drivers up to 4, above which per-driver rate * number of drivers,
      + per-passenger rate * number of passengers
    - Subtract largest of (coupon discount, customer discount, promotional discount, military discount, one-time discount)
    - Add sales tax
    """
    num_drivers: int = None
    num_passengers: int = None

    def __init__(self, num_drivers: int, num_passengers: int, **kwargs):
        self.num_drivers = num_drivers
        self.num_passengers = num_passengers
        super().__init__(**kwargs)

        # Start by calculating the base price
        self.subtotal = self.base_price

        # Find and apply greatest specific discount available
        self.calculate_specific_discount(value=self.subtotal)
        self.subtotal = self.apply_discount(value=self.specific_discount)
        self.post_specific_discount_subtotal = self.subtotal

    @property
    def driver_cost(self) -> float:
        if not self.num_drivers:
            return 0
        if self.num_drivers == 1:
            return settings.PERFORMANCE_EXPERIENCE_PRICES['1_drv']
        if self.num_drivers == 2:
            return settings.PERFORMANCE_EXPERIENCE_PRICES['2_drv']
        if self.num_drivers == 3:
            return settings.PERFORMANCE_EXPERIENCE_PRICES['3_drv']
        if self.num_drivers == 4:
            return settings.PERFORMANCE_EXPERIENCE_PRICES['4_drv']
        return settings.PERFORMANCE_EXPERIENCE_PRICES['cost_per_drv_gt_4'] * self.num_drivers

    @property
    def passenger_cost(self) -> float:
        if not self.num_passengers:
            return 0
        return settings.PERFORMANCE_EXPERIENCE_PRICES['cost_per_pax'] * self.num_passengers

    @property
    def base_price(self) -> float:
        return self.driver_cost + self.passenger_cost

    def get_price_data(self) -> dict:
        return dict(
            num_drivers=self.num_drivers,
            num_passengers=self.num_passengers,
            driver_cost=self.driver_cost,
            passenger_cost=self.passenger_cost,

            tax_zip=self.tax_zip,
            tax_rate=self.tax_rate.total_rate,
            tax_rate_as_percent=self.tax_rate.total_rate * 100,
            customer_id=self.customer.id if self.customer else None,
            base_price=quantize_currency(self.base_price),

            promotion_discount=quantize_currency(self.promotion_discount),
            coupon_discount=quantize_currency(self.coupon_discount),
            customer_discount=quantize_currency(self.customer_discount),
            military_discount=quantize_currency(self.military_discount),
            one_time_discount=quantize_currency(self.one_time_discount),
            specific_discount=quantize_currency(self.specific_discount),
            specific_discount_label=self.specific_discount_label,

            subtotal=quantize_currency(self.pre_tax_subtotal),
            computed_subtotal=quantize_currency(self.computed_subtotal),
            total_with_tax=quantize_currency(self.total_with_tax),
            tax_amount=quantize_currency(self.get_tax_amount()),
        )


class JoyRidePriceCalculator(PriceCalculator):
    """
    Price is calculated as follows:
    - Calculator is inited with # passengers, coupon code, email, and tax zip
    - Base price is predefined per number of passengers up to 4, above which per-passenger rate * number of passengers
    - Subtract largest of (coupon discount, customer discount, promotional discount, military discount, one-time discount)
    - Add sales tax
    """
    num_passengers: int = None

    def __init__(self, num_passengers: int, **kwargs):
        self.num_passengers = num_passengers
        super().__init__(**kwargs)

        # Start by calculating the base price
        self.subtotal = self.base_price

        # Find and apply greatest specific discount available
        self.calculate_specific_discount(value=self.subtotal)
        self.subtotal = self.apply_discount(value=self.specific_discount)
        self.post_specific_discount_subtotal = self.subtotal

    @property
    def passenger_cost(self) -> float:
        if not self.num_passengers:
            return 0
        if self.num_passengers == 1:
            return settings.JOY_RIDE_PRICES['1_pax']
        if self.num_passengers == 2:
            return settings.JOY_RIDE_PRICES['2_pax']
        if self.num_passengers == 3:
            return settings.JOY_RIDE_PRICES['3_pax']
        if self.num_passengers == 4:
            return settings.JOY_RIDE_PRICES['4_pax']
        return settings.JOY_RIDE_PRICES['cost_per_pax_gt_4'] * self.num_passengers

    @property
    def base_price(self) -> float:
        return self.passenger_cost

    def get_price_data(self) -> dict:
        return dict(
            num_drivers=0,
            num_passengers=self.num_passengers,
            driver_cost=0,
            passenger_cost=self.passenger_cost,

            tax_zip=self.tax_zip,
            tax_rate=self.tax_rate.total_rate,
            tax_rate_as_percent=self.tax_rate.total_rate * 100,
            customer_id=self.customer.id if self.customer else None,
            base_price=quantize_currency(self.base_price),

            promotion_discount=quantize_currency(self.promotion_discount),
            coupon_discount=quantize_currency(self.coupon_discount),
            customer_discount=quantize_currency(self.customer_discount),
            military_discount=quantize_currency(self.military_discount),
            one_time_discount=quantize_currency(self.one_time_discount),
            specific_discount=quantize_currency(self.specific_discount),
            specific_discount_label=self.specific_discount_label,

            subtotal=quantize_currency(self.pre_tax_subtotal),
            computed_subtotal=quantize_currency(self.computed_subtotal),
            total_with_tax=quantize_currency(self.total_with_tax),
            tax_amount=quantize_currency(self.get_tax_amount()),
        )
