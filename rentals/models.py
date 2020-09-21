from django.db import models


class Vehicle(models.Model):

    class VehicleType(models.TextChoices):
        CAR = ('car', 'Car')
        BIKE = ('bike', 'Bike')

    make = models.CharField(max_length=255, blank=True)
    model = models.CharField(max_length=255, blank=True)
    vehicle_type = models.CharField(choices=VehicleType.choices, max_length=20, blank=True)
