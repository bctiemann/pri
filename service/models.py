from django.db import models


class ScheduledService(models.Model):
    pass


class IncidentalService(models.Model):
    pass


class ServiceItem(models.Model):
    pass


class Damage(models.Model):

    class Fault(models.IntegerChoices):
        NONE = (0, 'None')
        CUSTOMER = (1, 'Customer')
        US = (2, 'Us')

    vehicle = models.ForeignKey('fleet.Vehicle', null=True, blank=True, on_delete=models.SET_NULL, related_name='damaged_vehicles')
    title = models.CharField(max_length=255, blank=True)
    damaged_at = models.DateTimeField(null=True, blank=True)
    repaired_at = models.DateTimeField(null=True, blank=True)
    is_repaired = models.BooleanField(default=False)
    cost = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    fault = models.IntegerField(choices=Fault.choices, null=True, blank=True)
    customer_billed_amount = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    customer_paid_amount = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    in_house_repair = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
