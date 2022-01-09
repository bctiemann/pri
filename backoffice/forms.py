import datetime
import pytz
import decimal

from django.conf import settings
from django import forms
from phonenumber_field.formfields import PhoneNumberField

from fleet.models import Vehicle, VehicleMarketing, VehiclePicture, VehicleVideo, VehicleType
from consignment.models import Consigner
from users.models import User, Employee, Customer
from sales.models import Reservation, Rental, Coupon
from sales.enums import (
    TRUE_FALSE_CHOICES, DELIVERY_REQUIRED_CHOICES, birth_years, operational_years, get_service_hours,
    current_year, get_exp_year_choices, get_exp_month_choices, get_vehicle_choices, get_extra_miles_choices
)


class CSSClassMixin:

    def add_widget_css_class(self, field, css_class_name):
        widget_css_class = self.fields[field].widget.attrs.get('class')
        widget_css_classes = widget_css_class.split(' ') if widget_css_class else []
        widget_css_classes.append(css_class_name)
        css_class_string = ' '.join(list(set(widget_css_classes)))
        self.fields[field].widget.attrs['class'] = css_class_string


# TODO: Add slug to the visible form fields and set on both models

class VehicleForm(CSSClassMixin, forms.ModelForm):
    WEIGHTING_CHOICES = (
        (0, '0 - Normal'),
        (1, '+1'),
        (2, '+2'),
        (3, '+3'),
    )

    external_owner = forms.ModelChoiceField(queryset=Consigner.objects.all(), empty_label='PRI', required=False)
    weighting = forms.ChoiceField(choices=WEIGHTING_CHOICES)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.add_widget_css_class('policy_phone', 'phone')

        for field in [
            'year', 'plate', 'mileage',
        ]:
            self.add_widget_css_class(field, 'short')

    class Meta:
        model = Vehicle
        exclude = ('slug', 'vehicle_marketing_id',)


class VehicleMarketingForm(CSSClassMixin, forms.ModelForm):
    tight_fit = forms.TypedChoiceField(coerce=lambda x: x == 'True', initial=False, choices=TRUE_FALSE_CHOICES)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in [
            'horsepower', 'torque', 'top_speed', 'gears', 'price_per_day',
            'discount_2_day', 'discount_3_day', 'discount_7_day', 'security_deposit', 'miles_included',
        ]:
            self.add_widget_css_class(field, 'short')

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


class ReservationDateTimeMixin:

    def init_reservation_date_time(self):
        if self.instance.out_at and self.instance.back_at:
            out_at_localized = self.instance.out_at.astimezone(pytz.timezone(settings.TIME_ZONE))
            back_at_localized = self.instance.back_at.astimezone(pytz.timezone(settings.TIME_ZONE))
            self.fields['out_at_date'].initial = out_at_localized.strftime('%m/%d/%Y')
            self.fields['back_at_date'].initial = back_at_localized.strftime('%m/%d/%Y')
            self.fields['out_at_time'].initial = out_at_localized.strftime('%H:%M')
            self.fields['back_at_time'].initial = back_at_localized.strftime('%H:%M')

    def clean(self):
        super().clean()
        out_at_time = datetime.datetime.strptime(self.cleaned_data['out_at_time'], '%H:%M').time()
        back_at_time = datetime.datetime.strptime(self.cleaned_data['back_at_time'], '%H:%M').time()
        self.cleaned_data['out_at'] = datetime.datetime.combine(
            self.cleaned_data['out_at_date'],
            out_at_time,
        )
        self.cleaned_data['back_at'] = datetime.datetime.combine(
            self.cleaned_data['back_at_date'],
            back_at_time,
        )


class ReservationForm(ReservationDateTimeMixin, CSSClassMixin, forms.ModelForm):

    customer = forms.ModelChoiceField(queryset=Customer.objects.all(), widget=forms.HiddenInput())
    reservation = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    email = forms.EmailField(required=False)
    home_phone = PhoneNumberField(required=False)
    work_phone = PhoneNumberField(required=False)
    mobile_phone = PhoneNumberField(required=False)

    out_at_date = forms.DateField(widget=forms.DateInput(attrs={'class': 'short check-conflict'}))
    out_at_time = forms.ChoiceField(choices=get_service_hours(), widget=forms.Select(attrs={'class': 'check-conflict'}))
    back_at_date = forms.DateField(widget=forms.DateInput(attrs={'class': 'short check-conflict'}))
    back_at_time = forms.ChoiceField(choices=get_service_hours(), widget=forms.Select(attrs={'class': 'check-conflict'}))

    delivery_required = forms.ChoiceField(choices=DELIVERY_REQUIRED_CHOICES)
    extra_miles = forms.ChoiceField(choices=get_extra_miles_choices())
    send_email = forms.ChoiceField(choices=TRUE_FALSE_CHOICES, required=False)
    is_military = forms.ChoiceField(choices=TRUE_FALSE_CHOICES, required=False)
    customer_notes = forms.CharField(widget=forms.Textarea(attrs={'class': 'customer-notes'}), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['vehicle'].choices = get_vehicle_choices()
        self.fields['vehicle'].widget.attrs['class'] = 'check-conflict'

        # Populate conditionally non-editable fields from linked customer
        phone_fields = ['home_phone', 'work_phone', 'mobile_phone']
        for field in ['first_name', 'last_name', 'email', 'home_phone', 'work_phone', 'mobile_phone']:
            field_classes = ['newuserfield']
            if self.instance.id:
                field_classes.append('dont-edit')
            if field in phone_fields:
                field_classes.append('phone')
            field_classes_str = ' '.join(field_classes)
            self.fields[field].widget.attrs['class'] = field_classes_str
            if self.instance.customer:
                if field in phone_fields:
                    self.fields[field].initial = getattr(self.instance.customer, field).as_national
                else:
                    self.fields[field].initial = getattr(self.instance.customer, field, None) or getattr(self.instance.customer.user, field, None)

        self.init_reservation_date_time()

        for field in ['drivers', 'delivery_zip', 'tax_percent', 'miles_included', 'coupon_code']:
            self.add_widget_css_class(field, 'short')

        self.fields['tax_percent'].initial = decimal.Decimal(settings.DEFAULT_TAX_RATE) * 100
        self.fields['override_subtotal'].widget.attrs['placeholder'] = 'Override'

    class Meta:
        model = Reservation
        # fields = '__all__'
        exclude = ('confirmation_code',)


class RentalForm(ReservationDateTimeMixin, CSSClassMixin, forms.ModelForm):

    out_at_date = forms.DateField(widget=forms.DateInput(attrs={'class': 'short check-conflict'}))
    out_at_time = forms.ChoiceField(choices=get_service_hours(), widget=forms.Select(attrs={'class': 'check-conflict'}))
    back_at_date = forms.DateField(widget=forms.DateInput(attrs={'class': 'short check-conflict'}))
    back_at_time = forms.ChoiceField(choices=get_service_hours(), widget=forms.Select(attrs={'class': 'check-conflict'}))

    delivery_required = forms.ChoiceField(choices=DELIVERY_REQUIRED_CHOICES)
    extra_miles = forms.ChoiceField(choices=get_extra_miles_choices())
    is_military = forms.ChoiceField(choices=TRUE_FALSE_CHOICES, required=False)
    customer_notes = forms.CharField(widget=forms.Textarea(attrs={'class': 'customer-notes'}), required=False)
    deposit_charged_on = forms.DateField(required=False)
    deposit_refunded_on = forms.DateField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['vehicle'].choices = get_vehicle_choices()
        self.fields['vehicle'].widget.attrs['class'] = 'check-conflict'

        for field in ['out_at_date', 'back_at_date']:
            if self.instance.status == Rental.Status.COMPLETE:
                self.add_widget_css_class(field, 'dont-edit')

        for field in [
            'delivery_zip', 'miles_included', 'mileage_out', 'mileage_back', 'coupon_code',
            'deposit_amount', 'deposit_charged_on', 'deposit_refund_amount', 'deposit_refunded_on',
            'rental_discount_pct', 'tax_percent'
        ]:
            self.add_widget_css_class(field, 'short')

        self.init_reservation_date_time()
        if self.instance.deposit_charged_at:
            deposit_charged_at_localized = self.instance.deposit_charged_at.astimezone(pytz.timezone(settings.TIME_ZONE))
            self.fields['deposit_charged_on'].initial = deposit_charged_at_localized.strftime('%m/%d/%Y')
        if self.instance.deposit_refunded_at:
            deposit_refunded_at_localized = self.instance.deposit_refunded_at.astimezone(pytz.timezone(settings.TIME_ZONE))
            self.fields['deposit_refunded_on'].initial = deposit_refunded_at_localized.strftime('%m/%d/%Y')

    def clean(self):
        super().clean()
        self.cleaned_data['deposit_charged_at'] = self.cleaned_data['deposit_charged_on']
        self.cleaned_data['deposit_refunded_at'] = self.cleaned_data['deposit_refunded_on']

    class Meta:
        model = Rental
        exclude = ('confirmation_code', 'customer',)


class EmployeeForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput(), required=True)
    date_of_birth = forms.DateField(widget=forms.SelectDateWidget(years=birth_years))

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exclude(pk=self.instance.user.id).exists():
            raise forms.ValidationError(f'A user with email {email} already exists.')

    class Meta:
        model = Employee
        # fields = '__all__'
        exclude = ('user',)


class CustomerForm(CSSClassMixin, forms.ModelForm):

    email = forms.EmailField(required=True)
    receive_email = forms.TypedChoiceField(coerce=lambda x: x == 'True', initial=False, choices=TRUE_FALSE_CHOICES)
    cc_exp_yr = forms.ChoiceField(choices=get_exp_year_choices(since_founding=True, allow_null=False))
    cc_exp_mo = forms.ChoiceField(choices=get_exp_month_choices(allow_null=False))
    cc2_exp_yr = forms.ChoiceField(choices=get_exp_year_choices(since_founding=True, allow_null=True), required=False)
    cc2_exp_mo = forms.ChoiceField(choices=get_exp_month_choices(allow_null=True), required=False)
    date_of_birth = forms.DateField(widget=forms.SelectDateWidget(years=birth_years))
    ban = forms.BooleanField(required=False)
    password = forms.CharField(widget=forms.PasswordInput(), required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.user:
            self.fields['email'].initial = self.instance.user.email
        phone_fields = ['home_phone', 'work_phone', 'mobile_phone', 'fax', 'insurance_company_phone', 'cc_phone', 'cc2_phone']
        for field in phone_fields:
            self.fields[field].widget.attrs['class'] = 'phone'
        cc_fields = ['cc_number', 'cc2_number']
        for field in cc_fields:
            self.fields[field].widget.attrs['class'] = 'cc-field'
        short_fields = [
            'zip', 'home_phone', 'mobile_phone', 'work_phone', 'fax', 'insurance_company_phone', 'discount_pct',
            'cc_cvv', 'cc_phone', 'cc2_cvv', 'cc2_phone',
        ]
        for field in short_fields:
            self.add_widget_css_class(field, 'short')

    # def get_exp_year_choices(self):
    #     return ((year, year) for year in range(settings.COMPANY_FOUNDING_YEAR, current_year + 11))

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exclude(pk=self.instance.user.id).exists():
            raise forms.ValidationError(f'A user with email {email} already exists.')

    class Meta:
        model = Customer
        # fields = '__all__'
        exclude = ('user', 'rentals_count',)


class CloneCustomerForm(forms.ModelForm):

    clone_first_name = forms.CharField()
    clone_last_name = forms.CharField()
    clone_email = forms.EmailField()
    clone_duplicate_license = forms.BooleanField(required=False)

    class Meta:
        model = Customer
        fields = ('clone_first_name', 'clone_last_name', 'clone_email', 'clone_duplicate_license',)


class CouponForm(forms.ModelForm):

    class Meta:
        model = Coupon
        fields = '__all__'