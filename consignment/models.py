import decimal

import pytz
from encrypted_fields import fields
from itertools import chain

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.shortcuts import reverse

from sales.models import Rental


class Consigner(models.Model):
    user = models.OneToOneField('users.User', null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    first_name = models.CharField(_('first name'), max_length=30)
    last_name = models.CharField(_('last name'), max_length=30)

    notes = fields.EncryptedTextField(blank=True)
    account_number = fields.EncryptedCharField(max_length=255, blank=True)
    routing_number = fields.EncryptedCharField(max_length=255, blank=True)
    address = fields.EncryptedTextField(blank=True)

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def vehicle_names_with_links(self):
        vehicle_links = []
        for vehicle in self.vehicle_set.all():
            url = reverse('backoffice:vehicle-detail', kwargs={'pk': vehicle.id})
            vehicle_links.append(f'<a href="{url}">{vehicle.model}</a>')
        return ', '.join(vehicle_links)

    @property
    def revenue_history(self):
        # rental_qs = Rental.objects.filter(vehicle__in=self.vehicle_set.all()).annotate(dummy_amount=Value(None, output_field=models.IntegerField())).values_list('id', 'out_at', 'final_price_data', 'dummy_amount')
        # payment_qs = self.consignmentpayment_set.all().annotate(dummy_price_data=Value({}, output_field=models.JSONField())).values_list('id', 'paid_at', 'dummy_price_data', 'amount')
        # return rental_qs.union(payment_qs)
        rental_qs = Rental.objects.filter(vehicle__in=self.vehicle_set.all(), status=Rental.Status.COMPLETE)
        payment_qs = self.consignmentpayment_set.all()
        combined_history = list(chain(rental_qs, payment_qs))
        sorted_history = sorted(combined_history, key=lambda x: x.transaction_time)
        total_revenue = 0
        total_paid = 0
        for transaction in sorted_history:
            if transaction._meta.model_name == 'rental':
                total_revenue += decimal.Decimal(transaction.final_price_data['post_multi_day_discount_subtotal'])
            else:
                total_paid += decimal.Decimal(transaction.amount)
            transaction.running_total = total_revenue
        return {
            'history': sorted_history,
            'total_revenue': total_revenue,
            'total_paid': total_paid,
        }

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
    consigner = models.ForeignKey('consignment.Consigner', null=True, blank=True, on_delete=models.SET_NULL)
    paid_at = models.DateTimeField(null=True, blank=True)
    amount = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    method = models.CharField(max_length=50, blank=True)

    @property
    def transaction_time(self):
        return self.paid_at
