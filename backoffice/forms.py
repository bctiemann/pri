from django import forms
from django.utils import timezone

from fleet.models import Vehicle, VehicleMarketing, VehiclePicture, VehicleVideo
from consignment.models import Consigner
from users.models import Employee

TRUE_FALSE_CHOICES = (
    (True, 'Yes'),
    (False, 'No')
)
current_year = timezone.now().year
birth_years = range(current_year - 18, current_year - 100, -1)


# TODO: Add slug to the visible form fields and set on both models

class VehicleForm(forms.ModelForm):
    WEIGHTING_CHOICES = (
        (0, '0 - Normal'),
        (1, '+1'),
        (2, '+2'),
        (3, '+3'),
    )

    external_owner = forms.ModelChoiceField(queryset=Consigner.objects.all(), empty_label='PRI', required=False)
    weighting = forms.ChoiceField(choices=WEIGHTING_CHOICES)

    class Meta:
        model = Vehicle
        exclude = ('slug',)


class VehicleMarketingForm(forms.ModelForm):
    tight_fit = forms.TypedChoiceField(coerce=lambda x: x == 'True', initial=False, choices=TRUE_FALSE_CHOICES)

    class Meta:
        model = VehicleMarketing
        exclude = ('vehicle_id', 'slug', 'showcase_image', 'thumbnail_image', 'inspection_image', 'mobile_thumbnail_image',)


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


class VehicleMobileThumbForm(forms.ModelForm):

    class Meta:
        model = VehicleMarketing
        fields = ('mobile_thumbnail_image',)


class VehiclePictureForm(forms.ModelForm):

    # TODO: validate image and thumbnail (prevent saving if nothing uploaded)

    class Meta:
        model = VehiclePicture
        fields = ('image',)


class VehicleVideoForm(forms.ModelForm):

    # TODO: validate video and thumbnail (prevent saving if nothing uploaded)

    class Meta:
        model = VehicleVideo
        fields = ('video_mp4', 'video_webm', 'poster', 'thumbnail', 'length', 'title', 'blurb',)


class EmployeeForm(forms.ModelForm):
    date_of_birth = forms.DateField(widget=forms.SelectDateWidget(years=birth_years))

    class Meta:
        model = Employee
        # fields = '__all__'
        exclude = ('user',)
