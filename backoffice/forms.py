from django import forms

from fleet.models import Vehicle, VehicleMarketing, VehiclePicture, VehicleVideo
from consignment.models import Consigner
from users.models import Employee


# TODO: Add slug to the visible form fields and set on both models

class VehicleForm(forms.ModelForm):
    external_owner = forms.ModelChoiceField(queryset=Consigner.objects.all(), empty_label='PRI', required=False)

    class Meta:
        model = Vehicle
        exclude = ('slug',)


class VehicleMarketingForm(forms.ModelForm):

    class Meta:
        model = VehicleMarketing
        exclude = ('vehicle_id', 'slug', 'showcase_image', 'thumbnail_image', 'inspection_image',)


class VehicleShowcaseForm(forms.ModelForm):

    class Meta:
        model = VehicleMarketing
        fields = ('showcase_image',)


class VehicleThumbnailForm(forms.ModelForm):

    class Meta:
        model = VehicleMarketing
        fields = ('thumbnail_image',)


class VehicleInspectionForm(forms.ModelForm):

    class Meta:
        model = VehicleMarketing
        fields = ('inspection_image',)


class VehiclePictureForm(forms.ModelForm):

    # TODO: validate image and thumbnail (prevent saving if nothing uploaded)

    class Meta:
        model = VehiclePicture
        fields = ('image',)


class VehicleVideoForm(forms.ModelForm):

    # TODO: validate video and thumbnail (prevent saving if nothing uploaded)

    class Meta:
        model = VehicleVideo
        fields = ('video', 'thumbnail', 'length', 'title', 'blurb',)


class EmployeeForm(forms.ModelForm):

    class Meta:
        model = Employee
        fields = '__all__'
