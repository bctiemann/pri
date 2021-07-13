from localflavor.us.models import USStateField, USZipCodeField

from django.db import models


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


class SalesTax(models.Model):
    pass


class Ban(models.Model):
    pass


class AdHocPayment(models.Model):
    pass


class Charge(models.Model):
    pass


class Discount(models.Model):
    pass
