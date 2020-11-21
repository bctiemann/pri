from django.db import models


class Vehicle(models.Model):

    # TextChoices and IntegerChoices are enum classes with internal and verbose values; if a CharField is set to use
    # this object for its choices, it will be represented in the admin with a select dropdown of acceptable values.
    class VehicleType(models.TextChoices):
        CAR = ('car', 'Road Car')
        BIKE = ('bike', 'Bike')
        TRACK = ('track', 'Track Car')

    class Status(models.IntegerChoices):
        BUILDING = (0, 'Building')
        READY = (1, 'Ready')
        DOWN = (2, 'Damaged / Repairing')
        OUT_OF_SERVICE = (3, 'Out Of Service')

    # Fields defined on the model correspond to database columns and fully define their behavior both in DB and in code.
    # Model field names should be verbose, specific, and expressive; i.e. "vehicle_type" rather than "vtype"
    # Note that an auto-incrementing integer "id" field is implicit in all models, unless overridden using the
    # "primary_key" parameter on a custom defined field
    # https://docs.djangoproject.com/en/3.1/ref/models/fields/
    make = models.CharField(max_length=255, blank=True)
    model = models.CharField(max_length=255, blank=True)
    year = models.IntegerField()
    vehicle_type = models.CharField(choices=VehicleType.choices, max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    acquired_on = models.DateField(null=True, blank=True)
    status = models.IntegerField(choices=Status.choices, default=Status.BUILDING.value)

    # Example of a model property which produces a derived value (requires no params other than self), and thus is
    # referenced as a property rather than being invoked as a method (with parentheses) - vehicle.vehicle_name
    @property
    def vehicle_name(self):
        return f'{self.year} {self.make} {self.model}'

    # Example of a model method taking one or more params - invoke like vehicle.is_available(date_start, date_end)
    def is_available(self, date_start, date_end):
        # logic to check availability goes here
        return True

    # This is the string representation of the vehicle object; will be used in the admin, templates, etc. as a default
    def __str__(self):
        return f'[{self.id}] {self.vehicle_name}'

    # Meta subclass is used for defining attributes like default ordering
    class Meta:
        ordering = ('year',)
