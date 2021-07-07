from django.db import models


class VehicleMarketing(models.Model):

    vehicle_id = models.IntegerField(null=True, blank=True)
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
        return self.id

    def __str__(self):
        return f'[{self.id}] {self.vehicle_name}'
