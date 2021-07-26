from django import forms

from fleet.models import Vehicle, VehicleMarketing


class VehicleForm(forms.ModelForm):

    class Meta:
        model = Vehicle
        fields = '__all__'


class VehicleMarketingForm(forms.ModelForm):

    class Meta:
        model = VehicleMarketing
        exclude = ('vehicle_id', 'slug',)
