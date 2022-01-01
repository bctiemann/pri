from rest_framework import serializers

from fleet.models import Vehicle, VehicleMarketing
from users.models import Customer


class VehicleSerializer(serializers.ModelSerializer):
    # TODO for migration: deprecate below listed specified fields
    vehicleid = serializers.IntegerField(source='id')
    type = serializers.IntegerField(source='vehicle_type')
    price = serializers.FloatField(source='price_per_day')  # TODO: Should be a DecimalField
    disc2day = serializers.IntegerField(source='discount_2_day')
    disc3day = serializers.IntegerField(source='discount_3_day')
    disc7day = serializers.IntegerField(source='discount_7_day')
    milesinc = serializers.IntegerField(source='miles_included')
    specs = serializers.CharField(source='specs_json')  # TODO: Should be a JSONField

    class Meta:
        model = VehicleMarketing
        fields = (
            'id', 'make', 'model', 'vehicle_type', 'price_per_day',
            'discount_2_day', 'discount_3_day', 'discount_7_day', 'miles_included', 'specs',
            # TODO: deprecate and remove below fields once mobile app is migrated to native field names
            'vehicleid', 'type', 'price', 'disc2day', 'disc3day', 'disc7day', 'milesinc',
        )


class VehicleDetailSerializer(serializers.ModelSerializer):
    extramiles = serializers.JSONField(source='extra_miles_choices')  # TODO: Should be extra_miles
    blurb = serializers.CharField(source='blurb_parsed')

    class Meta:
        model = VehicleMarketing
        fields = (
            'id', 'make', 'model', 'vehicle_type', 'price_per_day',
            'discount_2_day', 'discount_3_day', 'discount_7_day', 'miles_included', 'security_deposit', 'blurb', 'specs',
            'horsepower', 'torque', 'top_speed', 'transmission_type', 'gears', 'location', 'tight_fit', 'origin_country',
            'extramiles',
        )


class CustomerSearchSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(source='user.email')
    label = serializers.CharField(source='full_name')
    value = serializers.IntegerField(source='id')

    class Meta:
        model = Customer
        fields = (
            'label', 'value', 'id', 'first_name', 'last_name', 'email', 'home_phone', 'work_phone', 'mobile_phone',
        )