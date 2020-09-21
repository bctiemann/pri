from django.db import models


class Vehicle(models.Model):

    # TextChoices and IntegerChoices are enum classes with internal and verbose values; if a CharField is set to use
    # this object for its choices, it will be represented in the admin with a select dropdown of acceptable values.
    class VehicleType(models.TextChoices):
        CAR = ('car', 'Car')
        BIKE = ('bike', 'Bike')

    # Fields defined on the model correspond to database columns and fully define their behavior both in DB and in code.
    # Model field names should be verbose, specific, and expressive; i.e. "vehicle_type" rather than "vtype"
    make = models.CharField(max_length=255, blank=True)
    model = models.CharField(max_length=255, blank=True)
    vehicle_type = models.CharField(choices=VehicleType.choices, max_length=20, blank=True)

    # Example of a model property which produces a derived value (requires no params other than self)
    @property
    def vehicle_name(self):
        return f'{self.make} {self.model}'

    # Example of a model method taking one or more params - invoke like vehicle.is_available(date_start, date_end)
    def is_available(self, date_start, date_end):
        # logic to check availability goes here
        return True

    # This is the string representation of the vehicle object; will be used in the admin, templates, etc. as a default
    def __str__(self):
        return self.vehicle_name
