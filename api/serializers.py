from rest_framework import serializers

from fleet.models import Vehicle, VehicleMarketing


class VehicleSerializer(serializers.ModelSerializer):

    class Meta:
        model = VehicleMarketing
        fields = ('id', 'make', 'model', 'year',)
