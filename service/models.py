from django.db import models


class ScheduledService(models.Model):
    vehicle = models.ForeignKey('fleet.Vehicle', null=True, blank=True, on_delete=models.SET_NULL)
    service_item = models.ForeignKey('service.ServiceItem', null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=255, blank=True)
    done_at = models.DateTimeField(null=True, blank=True)
    done_mileage = models.IntegerField(null=True, blank=True)
    next_at = models.DateTimeField(null=True, blank=True)
    next_mileage = models.IntegerField(null=True, blank=True)
    is_due = models.BooleanField(default=False)
    notes = models.TextField(blank=True)


class IncidentalService(models.Model):
    vehicle = models.ForeignKey('fleet.Vehicle', null=True, blank=True, on_delete=models.SET_NULL)
    done_at = models.DateTimeField(null=True, blank=True)
    title = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    mileage = models.IntegerField(null=True, blank=True)


class ServiceItem(models.Model):
    name = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name


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
