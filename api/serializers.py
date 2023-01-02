from rest_framework import serializers
from django.urls import reverse
from phonenumber_field.phonenumber import PhoneNumber
from phonenumber_field.serializerfields import PhoneNumberField

from fleet.models import Vehicle, VehicleMarketing
from users.models import Customer
from sales.models import BaseReservation, Card


class NationalizedPhoneNumberField(PhoneNumberField):

    def to_representation(self, value):
        if isinstance(value, PhoneNumber):
            return value.as_national
        return value


class VehicleSerializer(serializers.ModelSerializer):
    # TODO for migration: deprecate below listed specified fields
    vehicleid = serializers.IntegerField(source='id')
    type = serializers.IntegerField(source='vehicle_type')
    price = serializers.DecimalField(source='price_per_day', max_digits=9, decimal_places=2)
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
    # TODO for migration: deprecate below listed specified fields
    vehicleid = serializers.IntegerField(source='id')
    type = serializers.IntegerField(source='vehicle_type')
    price = serializers.DecimalField(source='price_per_day', max_digits=9, decimal_places=2)
    disc2day = serializers.IntegerField(source='discount_2_day')
    disc3day = serializers.IntegerField(source='discount_3_day')
    disc7day = serializers.IntegerField(source='discount_7_day')
    milesinc = serializers.IntegerField(source='miles_included')
    specs = serializers.CharField(source='specs_json')  # TODO: Should be a JSONField
    hp = serializers.IntegerField(source='horsepower')
    tq = serializers.IntegerField(source='torque')
    deposit = serializers.DecimalField(source='security_deposit', max_digits=9, decimal_places=2)
    origin = serializers.CharField(source='origin_country')
    topspeed = serializers.IntegerField(source='top_speed')

    class Meta:
        model = VehicleMarketing
        fields = (
            'id', 'make', 'model', 'vehicle_type', 'price_per_day',
            'discount_2_day', 'discount_3_day', 'discount_7_day', 'miles_included', 'security_deposit', 'blurb', 'specs',
            'horsepower', 'torque', 'top_speed', 'transmission_type', 'gears', 'location', 'tight_fit', 'origin_country',
            'extramiles',
            # TODO: deprecate and remove below fields once mobile app is migrated to native field names
            'vehicleid', 'type', 'price', 'disc2day', 'disc3day', 'disc7day', 'milesinc', 'hp', 'tq', 'deposit',
            'origin', 'topspeed', 'type',
        )


class CustomerSearchSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(source='user.email')
    label = serializers.CharField(source='full_name')
    value = serializers.IntegerField(source='id')
    customer_url = serializers.SerializerMethodField()
    home_phone = NationalizedPhoneNumberField()
    work_phone = NationalizedPhoneNumberField()
    mobile_phone = NationalizedPhoneNumberField()

    def get_customer_url(self, obj):
        return reverse('backoffice:customer-detail', kwargs={'pk': obj.id})

    class Meta:
        model = Customer
        fields = (
            'label', 'value', 'id', 'first_name', 'last_name', 'email',
            'home_phone', 'work_phone', 'mobile_phone', 'customer_url',
        )


class ScheduleConflictSerializer(serializers.ModelSerializer):

    first_name = serializers.CharField(source='customer.first_name')
    last_name = serializers.CharField(source='customer.last_name')
    reservation_type = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    out_date = serializers.DateField(format='%m/%d/%Y')
    back_date = serializers.DateField(format='%m/%d/%Y')

    def get_reservation_type(self, obj):
        if obj.is_rental:
            return obj.ReservationType.RENTAL.label
        elif obj.is_reservation:
            return obj.ReservationType.RESERVATION.label

    def get_url(self, obj):
        if obj.is_reservation:
            return reverse('backoffice:reservation-detail', kwargs={'pk': obj.id})
        elif obj.is_rental:
            return reverse('backoffice:reservation-detail', kwargs={'pk': obj.id})

    class Meta:
        model = BaseReservation
        fields = (
            'id', 'is_reservation', 'is_rental', 'first_name', 'last_name', 'reservation_type',
            'out_date', 'back_date', 'reserved_at', 'num_days', 'url',
        )


class TaxRateFetchSerializer(serializers.Serializer):
    zip = serializers.CharField()
    force_refresh = serializers.BooleanField()


class CardSerializer(serializers.ModelSerializer):

    class Meta:
        model = Card
        fields = (
            'id',
            'stripe_card',
            'brand',
            'name',
            'last_4',
            'exp_month',
            'exp_year',
            'fingerprint',
        )
