import datetime

import pytz
import decimal

from django.conf import settings
from django import forms
from django.utils import timezone
from phonenumber_field.formfields import PhoneNumberField

from fleet.models import Vehicle, VehicleMarketing, VehiclePicture, VehicleVideo, VehicleType
from consignment.models import Consigner
from users.models import User, Employee, Customer
from sales.models import Reservation

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


class ReservationForm(forms.ModelForm):

    VEHICLE_CHOICES = []

    DELIVERY_REQUIRED_CHOICES = (
        (False, 'Pickup at PRI'),
        (True, 'Delivery'),
    )

    customer = forms.ModelChoiceField(queryset=Customer.objects.all(), widget=forms.HiddenInput())
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    email = forms.EmailField(required=False)
    home_phone = PhoneNumberField(required=False)
    work_phone = PhoneNumberField(required=False)
    mobile_phone = PhoneNumberField(required=False)
    out_at_date = forms.DateField(widget=forms.SelectDateWidget(attrs={'class': 'check-conflict'}))
    out_at_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time', 'class': 'check-conflict'}))
    back_at_date = forms.DateField(widget=forms.SelectDateWidget(attrs={'class': 'check-conflict'}))
    back_at_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time', 'class': 'check-conflict'}))
    delivery_required = forms.ChoiceField(choices=DELIVERY_REQUIRED_CHOICES)
    extra_miles = forms.ChoiceField()
    send_email = forms.ChoiceField(choices=TRUE_FALSE_CHOICES, required=False)
    is_military = forms.ChoiceField(choices=TRUE_FALSE_CHOICES, required=False)
    customer_notes = forms.CharField(widget=forms.Textarea(attrs={'class': 'customer-notes'}), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Populate vehicle choices
        self.VEHICLE_CHOICES = []
        self.VEHICLE_CHOICES.append(('Cars', list((v.id, v.vehicle_name) for v in VehicleMarketing.objects.filter(vehicle_type=VehicleType.CAR))))
        self.VEHICLE_CHOICES.append(('Motorcycles', list((v.id, v.vehicle_name) for v in VehicleMarketing.objects.filter(vehicle_type=VehicleType.BIKE))))
        self.fields['vehicle'].choices = self.VEHICLE_CHOICES

        # Populate conditionally non-editable fields from linked customer
        field_classes = ['newuserfield']
        if self.instance.id:
            field_classes.append('dont-edit')
        field_classes_str = ' '.join(field_classes)
        for field in ['first_name', 'last_name', 'email', 'home_phone', 'work_phone', 'mobile_phone']:
            self.fields[field].widget.attrs['class'] = field_classes_str
            if self.instance.customer:
                self.fields[field].initial = getattr(self.instance.customer, field, None) or getattr(self.instance.customer.user, field, None)

        if self.instance.out_at:
            out_at_localized = self.instance.out_at.astimezone(pytz.timezone(settings.TIME_ZONE))
            self.fields['out_at_date'].initial = out_at_localized
            self.fields['out_at_time'].initial = out_at_localized

        if self.instance.back_at:
            back_at_localized = self.instance.back_at.astimezone(pytz.timezone(settings.TIME_ZONE))
            self.fields['back_at_date'].initial = back_at_localized
            self.fields['back_at_time'].initial = back_at_localized

        for field in ['drivers', 'delivery_zip', 'tax_percent', 'miles_included', 'coupon_code']:
            self.fields[field].widget.attrs['class'] = 'short'

        self.fields['tax_percent'].initial = decimal.Decimal(settings.DEFAULT_TAX_RATE) * 100
        self.fields['extra_miles'].choices = ((k, v['label']) for k, v in settings.EXTRA_MILES_PRICES.items())
        self.fields['override_subtotal'].widget.attrs['placeholder'] = 'Override'

    def clean(self):
        self.cleaned_data['out_at'] = datetime.datetime.combine(
            self.cleaned_data['out_at_date'],
            self.cleaned_data['out_at_time'],
        )
        self.cleaned_data['back_at'] = datetime.datetime.combine(
            self.cleaned_data['back_at_date'],
            self.cleaned_data['back_at_time'],
        )

    class Meta:
        model = Reservation
        # fields = '__all__'
        exclude = ('confirmation_code',)


class EmployeeForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput(), required=True)
    date_of_birth = forms.DateField(widget=forms.SelectDateWidget(years=birth_years))

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(f'A user with email {email} already exists.')

    class Meta:
        model = Employee
        # fields = '__all__'
        exclude = ('user',)
