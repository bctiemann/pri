import pytz
from encrypted_fields import fields

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Consigner(models.Model):
    user = models.OneToOneField('users.User', null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    id_old = models.IntegerField(null=True, blank=True)

    first_name = models.CharField(_('first name'), max_length=30)
    last_name = models.CharField(_('last name'), max_length=30)

    notes = fields.EncryptedTextField(blank=True)
    account_number = fields.EncryptedCharField(max_length=255, blank=True)
    routing_number = fields.EncryptedCharField(max_length=255, blank=True)
    address = fields.EncryptedTextField(blank=True)

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return f'[{self.id}] {self.full_name}'


class ConsignmentReservation(models.Model):
    consigner = models.ForeignKey('consignment.Consigner', null=True, blank=True, on_delete=models.SET_NULL)
    vehicle = models.ForeignKey('fleet.Vehicle', null=True, blank=True, on_delete=models.SET_NULL)
    reserved_at = models.DateTimeField(auto_now_add=True)
    out_at = models.DateTimeField(null=True, blank=True)
    back_at = models.DateTimeField(null=True, blank=True)

    @property
    def out_date(self):
        return self.out_at.astimezone(pytz.timezone(settings.TIME_ZONE)).date()

    @property
    def back_date(self):
        return self.back_at.astimezone(pytz.timezone(settings.TIME_ZONE)).date()


class ConsignmentPayment(models.Model):
    pass
