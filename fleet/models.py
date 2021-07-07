from django_countries.fields import CountryField

from django.db import models


# TextChoices and IntegerChoices are enum classes with internal and verbose values; if a CharField is set to use
# this object for its choices, it will be represented in the admin with a select dropdown of acceptable values.
class VehicleType(models.TextChoices):
    CAR = ('car', 'Road Car')
    BIKE = ('bike', 'Bike')
    TRACK = ('track', 'Track Car')


class VehicleStatus(models.IntegerChoices):
    BUILDING = (0, 'Building')
    READY = (1, 'Ready')
    DOWN = (2, 'Damaged / Repairing')
    OUT_OF_SERVICE = (3, 'Out Of Service')


class TransmissionTypeChoices(models.TextChoices):
    MANUAL = ('manual', 'Manual')  # 1
    SEMI_AUTO = ('semi_auto', 'Semi-Auto')  # 2
    AUTO = ('auto', 'Automatic')  # 3


class LocationChoices(models.TextChoices):
    NEW_YORK = ('new_york', 'New York')
    TAMPA = ('tampa', 'Tampa')


class VehicleMarketing(models.Model):

    # This links the record to the backoffice Vehicle object, which is where potentially sensitive business data
    # is stored. Cannot be a ForeignKey because the databases are kept segregated.
    vehicle_id = models.IntegerField(null=True, blank=True, help_text='ID of backoffice Vehicle object this corresponds to')

    # These fields are redundant with the backoffice Vehicle class, and will be updated concurrently with that
    # table when edited via the backoffice form. This is to avoid any joins or queries against the Vehicle table
    # when pulling data for the front-end site.
    make = models.CharField(max_length=255, blank=True)
    model = models.CharField(max_length=255, blank=True)
    year = models.IntegerField(null=True, blank=True)
    vehicle_type = models.CharField(choices=VehicleType.choices, max_length=20, blank=True)
    status = models.IntegerField(choices=VehicleStatus.choices, blank=True)

    # These fields are for public display/marketing purposes only and are not sensitive.
    horsepower = models.IntegerField(null=True, blank=True)
    torque = models.IntegerField(null=True, blank=True)
    top_speed = models.IntegerField(null=True, blank=True)
    transmission_type = models.CharField(choices=TransmissionTypeChoices.choices, max_length=12, blank=True)
    gears = models.IntegerField(null=True, blank=True)
    location = models.CharField(choices=LocationChoices.choices, max_length=12, blank=True, default=LocationChoices.NEW_YORK)
    tight_fit = models.BooleanField(default=False)
    blurb = models.TextField(blank=True)
    specs = models.JSONField(null=True, blank=True, help_text='JSON format')
    origin_country = CountryField(blank=True)

    # Price fields
    price_per_day = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    discount_2_day = models.IntegerField(null=True, blank=True, verbose_name='2-day discount', help_text='Percent')
    discount_3_day = models.IntegerField(null=True, blank=True, verbose_name='3-day discount', help_text='Percent')
    discount_7_day = models.IntegerField(null=True, blank=True, verbose_name='7-day discount', help_text='Percent')
    deposit = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    miles_included = models.IntegerField(null=True, blank=True, help_text='Per day')

    @property
    def vehicle_name(self):
        return f'{self.year} {self.make} {self.model}'

    def __str__(self):
        return f'[{self.id}] {self.vehicle_name}'
