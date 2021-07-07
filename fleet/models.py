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


class VehicleMarketing(models.Model):

    # This links the record to the backoffice Vehicle object, which is where potentially sensitive business data
    # is stored. Cannot be a ForeignKey because the databases are kept segregated.
    vehicle_id = models.IntegerField(null=True, blank=True)
    # These fields are redundant with the backoffice Vehicle class, and will be updated concurrently with that
    # table when edited via the backoffice form. This is to avoid any joins with the Vehicle table when pulling
    # data for the front-end site.
    make = models.CharField(max_length=255, blank=True)
    model = models.CharField(max_length=255, blank=True)
    year = models.IntegerField(null=True, blank=True)
    vehicle_type = models.CharField(choices=VehicleType.choices, max_length=20, blank=True)
    status = models.IntegerField(choices=VehicleStatus.choices, blank=True)
    # These fields are for public display/marketing purposes only and are not sensitive.
    """
    # <CFQUERYPARAM value="#vars.vehicleid#" CFSQLType="CF_SQL_NUMERIC">,
    # <CFQUERYPARAM value="#Form.type#" CFSQLType="CF_SQL_NUMERIC">,
    <CFQUERYPARAM value="#Form.hp#" CFSQLType="CF_SQL_NUMERIC" null="#YesNoFormat(Form.hp IS '')#">,
    <CFQUERYPARAM value="#Form.tq#" CFSQLType="CF_SQL_NUMERIC" null="#YesNoFormat(Form.tq IS '')#">,
    <CFQUERYPARAM value="#Form.topspeed#" CFSQLType="CF_SQL_NUMERIC" null="#YesNoFormat(Form.topspeed IS '')#">,
    <CFQUERYPARAM value="#Form.trans#" CFSQLType="CF_SQL_NUMERIC">,
    <CFQUERYPARAM value="#Form.gears#" CFSQLType="CF_SQL_NUMERIC" null="#YesNoFormat(Form.gears IS '')#">,
    <CFQUERYPARAM value="#Form.status#" CFSQLType="CF_SQL_NUMERIC">,
    <CFQUERYPARAM value="#Form.location#" CFSQLType="CF_SQL_NUMERIC">,
    <CFQUERYPARAM value="#Form.tightfit#" CFSQLType="CF_SQL_NUMERIC">,
    <CFQUERYPARAM value="#Form.blurb#" CFSQLType="CF_SQL_VARCHAR">,
    <CFQUERYPARAM value="#Form.specs#" CFSQLType="CF_SQL_VARCHAR">,
    <CFQUERYPARAM value="#Form.origin#" CFSQLType="CF_SQL_CHAR" maxlength="2">,
    <CFQUERYPARAM value="#Form.price#" CFSQLType="CF_SQL_NUMERIC" SCALE="2" null="#YesNoFormat(Form.price IS '')#">,
    <CFQUERYPARAM value="#Form.disc2day#" CFSQLType="CF_SQL_NUMERIC" null="#YesNoFormat(Form.disc2day IS '')#">,
    <CFQUERYPARAM value="#Form.disc3day#" CFSQLType="CF_SQL_NUMERIC" null="#YesNoFormat(Form.disc3day IS '')#">,
    <CFQUERYPARAM value="#Form.disc7day#" CFSQLType="CF_SQL_NUMERIC" null="#YesNoFormat(Form.disc7day IS '')#">,
    <CFQUERYPARAM value="#Form.deposit#" CFSQLType="CF_SQL_NUMERIC" SCALE="2" null="#YesNoFormat(Form.deposit IS '')#">,
    <CFQUERYPARAM value="#Form.milesinc#" CFSQLType="CF_SQL_NUMERIC" null="#YesNoFormat(Form.milesinc IS '')#">
    """

    @property
    def vehicle_name(self):
        return f'{self.year} {self.make} {self.model}'

    def __str__(self):
        return f'[{self.id}] {self.vehicle_name}'
