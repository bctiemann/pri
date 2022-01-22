import datetime
import json
import pytz
import decimal
import random
import uuid
from localflavor.us.models import USStateField, USZipCodeField
from avalara import AvataxClient
from requests import HTTPError
from encrypted_fields import fields
from phonenumber_field.modelfields import PhoneNumberField
from django_countries.fields import CountryField
from django_countries import Countries

from django.conf import settings
from django.db import models
from django.utils.timezone import now
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import reverse

from sales.enums import RESERVATION_TYPE_CODE_MAP, ReservationType, ServiceType
from sales.utils import EncryptedUSSocialSecurityNumberField, format_cc_number


def generate_code(reservation_type):
    alpha_str = ''.join(random.choice('123456789ABCNPQDXEFGHJKMVZ') for _ in range(4))
    numeric_str = random.randrange(10, 100)
    return f'{RESERVATION_TYPE_CODE_MAP.get(reservation_type)}{alpha_str}{numeric_str}'


class AllCountries(Countries):
    only = []
    first = ['US', 'CA']

# class ServiceType(models.TextChoices):
#     RENTAL = ('rental', 'Rental')
#     PERFORMANCE_EXPERIENCE = ('perfexp', 'Performance Experience')
#     JOY_RIDE = ('joyride', 'Joy Ride')
#     GIFT_CERTIFICATE = ('giftcert', 'Gift Certificate')


# Promotions are time-bound discounts that apply to all customers, such as a holiday special. They may or may not
# be restricted to a certain service type (such as Performance Experiences only).
# Typically only one Promotion should be active at a given time, though this is not currently enforced in code and the
# behavior if multiple Promotions are active is to choose the first valid one in the database.
class Promotion(models.Model):
    name = models.CharField(max_length=255, blank=True)
    amount = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    percent = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    service_type = models.CharField(max_length=50, choices=ServiceType.choices, blank=True)

    @property
    def value_str(self):
        if self.amount:
            return f'${self.amount}'
        if self.percent:
            return f'{self.percent}%'

    def get_discount_value(self, value):
        if self.amount:
            return self.amount
        elif self.percent:
            return value * float(self.percent) / 100
        return 0

    def get_discounted_value(self, value):
        return value - self.get_discount_value(value)

    def is_expired_on(self, effective_date):
        if effective_date is None:
            return False
        if self.end_date is None:
            return False
        return effective_date > self.end_date

    def __str__(self):
        return f'{self.name} ({self.value_str})'


# A Coupon is a Promotion that is identified by a code that a customer has to enter. It also differs from a Promotion
# in that it might or might not have an end date (expiration date), and if it has a start date it will be ignored.
# Many coupons can be active at the same time.
class Coupon(Promotion):
    code = models.CharField(max_length=50, unique=True, db_index=True)

    def save(self, *args, **kwargs):
        self.code = self.code.upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.code} ({self.value_str})'


# Concrete base model class which is used to supply common fields to both the Reservation and Rental model classes.
# Don't want to use an abstract model class because we want to be able to query both tables simultaneously in a union

class BaseReservation(models.Model):

    class AppChannel(models.TextChoices):
        WEB = ('web', 'Web')
        MOBILE = ('mobile', 'Mobile')
        PHONE = ('phone', 'Phone')

    class ReservationType(models.TextChoices):
        RESERVATION = ('reservation', 'Unconfirmed Reservation')
        RENTAL = ('rental', 'Confirmed Rental')

    type = models.CharField(max_length=20, choices=ReservationType.choices, blank=True, default=ReservationType.RESERVATION)
    vehicle = models.ForeignKey('fleet.Vehicle', null=True, blank=True, on_delete=models.SET_NULL)
    customer = models.ForeignKey('users.Customer', null=True, blank=True, on_delete=models.SET_NULL)
    reserved_at = models.DateTimeField(auto_now_add=True)
    out_at = models.DateTimeField(null=True, blank=True)
    back_at = models.DateTimeField(null=True, blank=True)
    drivers = models.IntegerField(null=True, blank=True)
    miles_included = models.IntegerField(null=True, blank=True)
    extra_miles = models.IntegerField(null=True, blank=True)
    customer_notes = models.TextField(blank=True)
    coupon_code = models.CharField(max_length=30, blank=True)
    is_military = models.BooleanField(default=False)
    deposit_amount = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    confirmation_code = models.CharField(max_length=10, blank=True)
    app_channel = models.CharField(max_length=20, choices=AppChannel.choices, blank=True, default=AppChannel.WEB)
    delivery_required = models.BooleanField(default=False)
    delivery_zip = USZipCodeField(blank=True)
    override_subtotal = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    final_price_data = models.JSONField(null=True, blank=True)

    @property
    def is_reservation(self):
        try:
            return bool(self.reservation)
        except Reservation.DoesNotExist:
            return False

    @property
    def is_rental(self):
        try:
            return bool(self.rental)
        except Rental.DoesNotExist:
            return False

    @property
    def out_date(self):
        if self.out_at:
            return self.out_at.astimezone(pytz.timezone(settings.TIME_ZONE)).date()
        return None

    @property
    def back_date(self):
        if self.back_at:
            return self.back_at.astimezone(pytz.timezone(settings.TIME_ZONE)).date()
        return None

    @property
    def num_days(self):
        if self.out_at and self.back_at:
            # Pad the selection with 30m so the estimate comes out to 1 day if up to 24.5 hours
            grace_period = datetime.timedelta(seconds=1801)
            rental_length = (self.back_at - self.out_at - grace_period)
            return int(rental_length.days) + 1
        return 0

    @property
    def coupon(self):
        if self.coupon_code and self.out_date:
            return Coupon.objects.filter(models.Q(end_date__isnull=True) | models.Q(end_date__gte=self.out_date), code=self.coupon_code).first()
        return None

    @property
    def transaction_time(self):
        return self.out_at

    def get_price_data(self):
        # TODO: Refactor sales.models classes to avoid this nested import
        from sales.calculators import RentalPriceCalculator
        price_calculator = RentalPriceCalculator(
            coupon_code=self.coupon_code,
            email=self.customer.email,
            tax_zip=self.delivery_zip or settings.DEFAULT_TAX_ZIP,
            effective_date=self.out_date,
            is_military=self.is_military,
            vehicle_marketing=self.vehicle.vehicle_marketing,
            num_days=self.num_days,
            extra_miles=self.extra_miles,
            override_subtotal=self.override_subtotal,
            one_time_discount_pct=getattr(self, 'rental_discount_pct', None),
        )
        return price_calculator.get_price_data()

    def save(self, *args, **kwargs):
        self.coupon_code = self.coupon_code.upper()
        self.final_price_data = json.loads(json.dumps(self.get_price_data(), cls=DjangoJSONEncoder))
        super().save(*args, **kwargs)

    class Meta:
        abstract = False
        unique_together = ('confirmation_code', 'type',)


class Reservation(BaseReservation):

    class Status(models.IntegerChoices):
        UNCONFIRMED = (0, 'Unconfirmed')
        CONFIRMED = (1, 'Confirmed')

    status = models.IntegerField(choices=Status.choices, default=Status.UNCONFIRMED)


class Rental(BaseReservation):

    class Status(models.IntegerChoices):
        INCOMPLETE = (0, 'Incomplete')
        CONFIRMED = (1, 'Confirmed/Billed')
        IN_PROGRESS = (2, 'In Progress')
        COMPLETE = (3, 'Complete')
        CANCELLED = (4, 'Cancelled')

    status = models.IntegerField(choices=Status.choices, default=Status.INCOMPLETE, blank=True)
    background_check = models.BooleanField(default=False)
    mileage_out = models.IntegerField(null=True, blank=True)
    mileage_back = models.IntegerField(null=True, blank=True)
    abuse = models.TextField(blank=True)
    damage_out = models.TextField(blank=True)
    damage_in = models.TextField(blank=True)
    internal_notes = fields.EncryptedTextField(blank=True)
    deposit_charged_at = models.DateTimeField(null=True, blank=True)
    deposit_refunded_at = models.DateTimeField(null=True, blank=True)
    deposit_refund_amount = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    rental_discount_pct = models.IntegerField(null=True, blank=True)
    extended_days = models.IntegerField(null=True, blank=True)

    @property
    def extended_days_amount(self):
        return self.extended_days * self.vehicle.vehicle_marketing.price_per_day


class Driver(models.Model):
    rental = models.ForeignKey('sales.Rental', on_delete=models.CASCADE)
    customer = models.ForeignKey('users.Customer', on_delete=models.CASCADE)
    is_primary = models.BooleanField(default=False)

    class Meta:
        ordering = ('-is_primary',)


class GuidedDrive(models.Model):

    class EventType(models.IntegerChoices):
        JOY_RIDE = (1, 'Joy Ride')
        PERFORMANCE_EXPERIENCE = (2, 'Performance Experience')

    class Status(models.IntegerChoices):
        PENDING = (0, 'Pending')
        CONFIRMED = (1, 'Confirmed/Billed')
        COMPLETE = (2, 'Complete')
        CANCELLED = (3, 'Cancelled')

    status = models.IntegerField(choices=Status.choices, default=Status.PENDING)
    customer = models.ForeignKey('users.Customer', null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    vehicle_choice_1 = models.ForeignKey('fleet.Vehicle', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    vehicle_choice_2 = models.ForeignKey('fleet.Vehicle', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    vehicle_choice_3 = models.ForeignKey('fleet.Vehicle', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    num_passengers = models.IntegerField(null=True, blank=True)
    num_minors = models.IntegerField(null=True, blank=True)
    requested_date = models.DateField(null=True, blank=True)
    backup_date = models.DateField(null=True, blank=True)
    customer_notes = models.TextField(blank=True)
    internal_notes = fields.EncryptedTextField(blank=True)
    big_and_tall = models.BooleanField(default=False)
    coupon_code = models.CharField(max_length=30, blank=True)
    event_type = models.IntegerField(choices=EventType.choices, default=EventType.JOY_RIDE, blank=True)
    confirmation_code = models.CharField(max_length=10, blank=True, unique=True)
    override_subtotal = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    final_price_data = models.JSONField(null=True, blank=True)

    @property
    def vehicle_list(self):
        vehicles = []
        for vehicle in [self.vehicle_choice_1, self.vehicle_choice_2, self.vehicle_choice_3]:
            if vehicle:
                vehicles.append(vehicle)
        return vehicles

    @property
    def vehicle_names_with_links(self):
        vehicle_links = []
        for vehicle in self.vehicle_list:
            url = reverse('backoffice:vehicle-detail', kwargs={'pk': vehicle.id})
            vehicle_links.append(f'<a href="{url}">{vehicle.model}</a>')
        return ', '.join(vehicle_links)

    @property
    def coupon(self):
        if self.coupon_code and self.requested_date:
            return Coupon.objects.filter(models.Q(end_date__isnull=True) | models.Q(end_date__gte=self.requested_date), code=self.coupon_code).first()
        return None

    def save(self, *args, **kwargs):
        self.coupon_code = self.coupon_code.upper()
        if self.id:
            self.final_price_data = json.loads(json.dumps(self.get_price_data(), cls=DjangoJSONEncoder))
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class JoyRide(GuidedDrive):

    def get_price_data(self):
        # TODO: Refactor sales.models classes to avoid this nested import
        from sales.calculators import JoyRidePriceCalculator
        price_calculator = JoyRidePriceCalculator(
            coupon_code=self.coupon_code,
            email=self.customer.email,
            tax_zip=settings.DEFAULT_TAX_ZIP,
            effective_date=self.requested_date,
            is_military=False,
            num_passengers=self.num_passengers,
            override_subtotal=self.override_subtotal,
        )
        return price_calculator.get_price_data()

    def get_confirmation_code(self):
        return generate_code(ReservationType.JOY_RIDE.value)



class PerformanceExperience(GuidedDrive):
    num_drivers = models.IntegerField(null=True, blank=True)

    def get_price_data(self):
        # TODO: Refactor sales.models classes to avoid this nested import
        from sales.calculators import PerformanceExperiencePriceCalculator
        price_calculator = PerformanceExperiencePriceCalculator(
            coupon_code=self.coupon_code,
            email=self.customer.email,
            tax_zip=settings.DEFAULT_TAX_ZIP,
            effective_date=self.requested_date,
            is_military=False,
            num_drivers=self.num_drivers,
            num_passengers=self.num_passengers,
            override_subtotal=self.override_subtotal,
        )
        return price_calculator.get_price_data()

    def get_confirmation_code(self):
        return generate_code(ReservationType.PERFORMANCE_EXPERIENCE.value)


class GiftCertificate(models.Model):
    tag = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    issued_at = models.DateTimeField(null=True, blank=True)
    beneficiary_name = models.CharField(max_length=255, blank=True)

    cc_name = models.CharField(max_length=255, null=True, blank=True)
    cc_address = fields.EncryptedCharField(max_length=255, null=True, blank=True)
    cc_city = models.CharField(max_length=255, blank=True)
    cc_state = USStateField(null=True, blank=True)
    cc_zip = USZipCodeField(null=True, blank=True)

    card = models.ForeignKey('sales.Card', null=True, blank=True, on_delete=models.SET_NULL)

    cc_number = fields.EncryptedCharField(max_length=255, blank=True, verbose_name='CC number')
    cc_exp_yr = models.CharField(max_length=4, blank=True, verbose_name='CC exp year')
    cc_exp_mo = models.CharField(max_length=2, blank=True, verbose_name='CC exp month')
    cc_cvv = models.CharField(max_length=6, blank=True, verbose_name='CC CVV')
    cc_phone = PhoneNumberField(blank=True, verbose_name='CC contact phone')

    email = models.EmailField(null=True, blank=True)
    phone = PhoneNumberField(blank=True)
    is_used = models.BooleanField(default=False)
    used_on = models.DateField(null=True, blank=True)
    remarks = fields.EncryptedTextField(blank=True)
    amount = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    message = models.CharField(max_length=200, blank=True)
    value_message = models.CharField(max_length=255, blank=True)

    def save(self, *args, **kwargs):
        self.cc_number = format_cc_number(self.cc_number)
        super().save(*args, **kwargs)


class TaxRate(models.Model):
    MAX_AGE_DAYS = 30

    postal_code = USZipCodeField(blank=True)
    country = models.CharField(max_length=20, default='us')
    total_rate = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True)
    detail = models.JSONField(null=True, blank=True)
    date_updated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{0}: {1}'.format(self.postal_code, self.total_rate)

    @property
    def total_rate_as_percent(self):
        if self.total_rate:
            return self.total_rate * 100
        return 0

    def update(self):
        client = AvataxClient(
            settings.AVALARA_APP_NAME,
            settings.AVALARA_APP_VERSION,
            settings.AVALARA_MACHINE_NAME,
            settings.AVALARA_ENVIRONMENT,
        )
        client.add_credentials(settings.AVALARA_ACCOUNT_ID, settings.AVALARA_LICENSE_KEY)
        try:
            response = client.tax_rates_by_postal_code(include={'country': self.country, 'postalCode': self.postal_code})
            response.raise_for_status()
            result = response.json()
            self.total_rate = result['totalRate']
            self.detail = result
            self.date_updated = now()
        except HTTPError:
            self.total_rate = decimal.Decimal(settings.DEFAULT_TAX_RATE)
        self.save()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.total_rate or (now() - self.date_updated).total_seconds() / 86400 > self.MAX_AGE_DAYS:
            self.update()


class RedFlag(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    full_name = models.CharField(max_length=255, blank=True)
    home_phone = PhoneNumberField(blank=True)
    mobile_phone = PhoneNumberField(blank=True)
    address = fields.EncryptedCharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, blank=True)
    state = USStateField(blank=True)
    zip = USZipCodeField(blank=True)
    email = models.EmailField(blank=True)
    license_number = models.CharField(max_length=30, blank=True)
    license_state = USStateField(blank=True)
    ssn = EncryptedUSSocialSecurityNumberField(null=True, blank=True)
    remarks = models.TextField(blank=True)


class AdHocPayment(models.Model):
    full_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_submitted = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    item = models.CharField(max_length=255, blank=True)
    message = models.TextField(blank=True)
    comments = models.TextField(blank=True)
    card = models.ForeignKey('sales.Card', null=True, blank=True, on_delete=models.SET_NULL)
    cc_number = fields.EncryptedCharField(max_length=255, blank=True, verbose_name='CC number')
    cc_exp_yr = models.CharField(max_length=4, blank=True, verbose_name='CC exp year')
    cc_exp_mo = models.CharField(max_length=2, blank=True, verbose_name='CC exp month')
    cc_cvv = models.CharField(max_length=6, blank=True, verbose_name='CC CVV')
    cc_address = fields.EncryptedCharField(max_length=255, null=True, blank=True)
    cc_city = models.CharField(max_length=255, blank=True)
    cc_state = USStateField(null=True, blank=True)
    cc_zip = USZipCodeField(null=True, blank=True)
    phone = PhoneNumberField(blank=True, verbose_name='CC contact phone')
    foreign_region = models.CharField(max_length=100, blank=True)
    country = CountryField(blank=True, countries=AllCountries)

    def save(self, *args, **kwargs):
        self.cc_number = format_cc_number(self.cc_number)
        super().save(*args, **kwargs)


class Charge(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4)
    full_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    capture = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    charged_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    card = models.ForeignKey('sales.Card', null=True, blank=True, on_delete=models.SET_NULL)
    cc_number = fields.EncryptedCharField(max_length=255, blank=True, verbose_name='CC number')
    cc_exp_yr = models.CharField(max_length=4, blank=True, verbose_name='CC exp year')
    cc_exp_mo = models.CharField(max_length=2, blank=True, verbose_name='CC exp month')
    cc_cvv = models.CharField(max_length=6, blank=True, verbose_name='CC CVV')
    cc_address = fields.EncryptedCharField(max_length=255, null=True, blank=True)
    cc_city = models.CharField(max_length=255, blank=True)
    cc_state = USStateField(null=True, blank=True)
    cc_zip = USZipCodeField(null=True, blank=True)
    phone = PhoneNumberField(blank=True, verbose_name='CC contact phone')
    foreign_region = models.CharField(max_length=100, blank=True)
    country = CountryField(blank=True, countries=AllCountries)
    processor_charge_id = models.CharField(max_length=50, blank=True)
    error_code = models.CharField(max_length=30, blank=True)

    @property
    def status(self):
        if self.processor_charge_id and not self.error_code:
            return 'success'
        elif self.error_code:
            return self.error_code
        return 'pending'

    def save(self, *args, **kwargs):
        self.cc_number = format_cc_number(self.cc_number)
        super().save(*args, **kwargs)


class Card(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey('users.Customer', null=True, blank=True, on_delete=models.SET_NULL)
    date_created = models.DateTimeField(auto_now_add=True)
    stripe_card = models.CharField(null=True, blank=True, max_length=30)
    fingerprint = models.CharField(null=True, blank=True, max_length=30)
    brand = models.CharField(null=True, blank=True, max_length=30)
    name = models.CharField(null=True, blank=True, max_length=30)
    last_4 = models.CharField(null=True, blank=True, max_length=4)
    is_primary = models.BooleanField(default=False)

    number = fields.EncryptedCharField(max_length=255, blank=True, verbose_name='CC number')
    exp_month = models.CharField(null=True, blank=True, max_length=2)
    exp_year = models.CharField(null=True, blank=True, max_length=4)
    cvv = models.CharField(max_length=6, blank=True, verbose_name='CC CVV')
    address = fields.EncryptedCharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, blank=True)
    state = USStateField(null=True, blank=True)
    zip = USZipCodeField(null=True, blank=True)
    phone = PhoneNumberField(blank=True, verbose_name='CC contact phone')

    def __str__(self):
        return '{0} ({1} {2})'.format(self.id, self.brand, self.last_4)

    def card_is_changed(self, number, exp_month, exp_year, cvv):
        return any((
            self.number != number,
            int(self.exp_month) != int(exp_month),
            (self.exp_year != exp_year and not settings.CARD_NUMBER_OVERRIDE),
            self.cvv != cvv,
        ))

    def save(self, *args, **kwargs):
        self.number = format_cc_number(self.number)
        super().save(*args, **kwargs)
