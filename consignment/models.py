from encrypted_fields import fields

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


class ConsignmentVehicle(models.Model):
    pass


class ConsignmentReservation(models.Model):
    pass


class ConsignmentPayment(models.Model):
    pass
