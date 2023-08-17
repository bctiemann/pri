from django.db import models


class LegacyVehicleFront(models.Model):
    vehicleid = models.IntegerField(primary_key=True)
    type = models.IntegerField(null=True, blank=True)
    status = models.IntegerField(null=True)
    hp = models.IntegerField(null=True, blank=True)
    tq = models.IntegerField(null=True, blank=True)
    topspeed = models.IntegerField(null=True, blank=True)
    trans = models.IntegerField(null=True, blank=True)
    gears = models.IntegerField(null=True, blank=True)
    location = models.IntegerField(null=True, blank=True)
    tightfit = models.BooleanField(default=False)
    blurb = models.TextField(blank=True)
    specs = models.TextField(blank=True)
    origin = models.CharField(max_length=2, blank=True)

    # Price fields
    price = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    disc2day = models.IntegerField(null=True, blank=True, verbose_name='2-day discount', help_text='Percent')
    disc3day = models.IntegerField(null=True, blank=True, verbose_name='3-day discount', help_text='Percent')
    disc7day = models.IntegerField(null=True, blank=True, verbose_name='7-day discount', help_text='Percent')
    deposit = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    milesinc = models.IntegerField(null=True, blank=True, help_text='Per day')

    class Meta:
        db_table = 'VehiclesFront'


class LegacyVehicle(models.Model):
    vehicleid = models.IntegerField(primary_key=True)
    make = models.CharField(max_length=255, blank=True)
    model = models.CharField(max_length=255, blank=True)
    year = models.IntegerField(null=True, blank=True)
    type = models.IntegerField(null=True, blank=True)
    status = models.IntegerField(null=True, blank=True)
    plate = models.CharField(max_length=10, blank=True)
    vin = models.CharField(max_length=50, blank=True)
    mileage = models.IntegerField(null=True, blank=True)
    damage = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    policyno = models.CharField(max_length=255, blank=True)
    policyco = models.CharField(max_length=255, blank=True)
    policytel = models.CharField(max_length=30, blank=True)
    weighting = models.IntegerField(null=True, blank=True)
    redirect = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'Vehicles'
