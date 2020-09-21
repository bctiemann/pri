from django.db import models


class Vehicle(models.Model):

    class VehicleType(models.TextChoices):
        CAR = ('car', 'Car')
        BIKE = ('bike', 'Bike')

    make = models.CharField(max_length=255, blank=True)
    model = models.CharField(max_length=255, blank=True)
    vehicle_type = models.CharField(choices=VehicleType.choices, max_length=20, blank=True)

    # Example of a model property which produces a derived value
    @property
    def vehicle_name(self):
        return f'{self.make} {self.model}'

    # Example of a model method taking one or more params - invoke like vehicle.is_available(date_start, date_end)
    def is_available(self, date_start, date_end):
        # logic to check availability goes here
        return True

    def __str__(self):
        return self.vehicle_name
