from django import forms

from fleet.models import Vehicle, VehicleMarketing
from consignment.models import Consigner


# TODO: Add slug to the visible form fields and set on both models

class VehicleForm(forms.ModelForm):
    external_owner = forms.ModelChoiceField(queryset=Consigner.objects.all(), empty_label='PRI', required=False)

    class Meta:
        model = Vehicle
        exclude = ('slug',)


class VehicleMarketingForm(forms.ModelForm):

    class Meta:
        model = VehicleMarketing
        exclude = ('vehicle_id', 'slug',)
