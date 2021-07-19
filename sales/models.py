import json
import decimal
from localflavor.us.models import USStateField, USZipCodeField
from avalara import AvataxClient
from requests import HTTPError

from django.conf import settings
from django.db import models
from django.utils.timezone import now


class Reservation(models.Model):

    class StatusChoices(models.IntegerChoices):
        UNCONFIRMED = (0, 'Unconfirmed')
        CONFIRMED = (1, 'Confirmed')

    vehicle = models.ForeignKey('fleet.Vehicle', null=True, blank=True, on_delete=models.SET_NULL)
    customer = models.ForeignKey('users.Customer', null=True, blank=True, on_delete=models.SET_NULL)
    id_old = models.IntegerField(null=True, blank=True)
    reserved_at = models.DateTimeField(auto_now_add=True)
    out_at = models.DateTimeField(null=True, blank=True)
    back_at = models.DateTimeField(null=True, blank=True)
    rate = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    drivers = models.IntegerField(null=True, blank=True)
    miles_included = models.IntegerField(null=True, blank=True)
    extra_miles = models.IntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)
    coupon_code = models.CharField(max_length=30, blank=True)
    status = models.IntegerField(choices=StatusChoices.choices, default=StatusChoices.UNCONFIRMED, blank=True)
    deposit_amount = models.IntegerField(null=True, blank=True)
    confirmation_code = models.CharField(max_length=10, blank=True)
    delivery_required = models.BooleanField(default=False)
    tax_percent = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True)
    delivery_zip = USZipCodeField(blank=True)


class Rental(models.Model):
    pass


class GuidedDrive(models.Model):
    pass


class Driver(models.Model):
    pass


class GiftCertificate(models.Model):
    pass


class TaxRate(models.Model):
    postal_code = USZipCodeField(blank=True)
    country = models.CharField(max_length=20, default='us')
    total_rate = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True)
    detail = models.JSONField(null=True, blank=True)
    date_updated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{0}: {1}'.format(self.postal_code, self.total_rate)

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
            self.detail = result['rates']
            self.date_updated = now()
        except HTTPError:
            self.total_rate = decimal.Decimal(settings.DEFAULT_TAX_RATE)
        self.save()


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.total_rate:
            self.update()


class Ban(models.Model):
    pass


class AdHocPayment(models.Model):
    pass


class Charge(models.Model):
    pass


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True, db_index=True)
    amount = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    percent = models.IntegerField(null=True, blank=True)

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
            return value * self.percent
        return 0

    def get_discounted_value(self, value):
        return value - self.get_discount_value(value)

    def __str__(self):
        return f'{self.code} ({self.value_str})'
