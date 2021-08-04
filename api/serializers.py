from rest_framework import serializers

from fleet.models import Vehicle, VehicleMarketing


class VehicleSerializer(serializers.ModelSerializer):
    # TODO for migration: deprecate below listed specified fields
    vehicleid = serializers.IntegerField(source='id')
    type = serializers.IntegerField(source='vehicle_type')
    price = serializers.DecimalField(source='price_per_day', max_digits=9, decimal_places=2)
    disc2day = serializers.IntegerField(source='discount_2_day')
    disc3day = serializers.IntegerField(source='discount_3_day')
    disc7day = serializers.IntegerField(source='discount_7_day')
    milesinc = serializers.IntegerField(source='miles_included')

    class Meta:
        model = VehicleMarketing
        fields = (
            'id', 'make', 'model', 'vehicle_type', 'price_per_day',
            'discount_2_day', 'discount_3_day', 'discount_7_day', 'miles_included', 'specs',
            # TODO: deprecate and remove below fields once mobile app is migrated to native field names
            'vehicleid', 'type', 'price', 'disc2day', 'disc3day', 'disc7day', 'milesinc',
        )
