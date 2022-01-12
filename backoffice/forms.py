import datetime
import pytz
import decimal

from django.conf import settings
from django import forms
from phonenumber_field.formfields import PhoneNumberField

from fleet.models import Vehicle, VehicleMarketing, VehiclePicture, VehicleVideo, TollTag
from consignment.models import Consigner, ConsignmentPayment
from users.models import User, Employee, Customer
from sales.models import Reservation, Rental, GuidedDrive, JoyRide, PerformanceExperience, Coupon, TaxRate, GiftCertificate
from sales.enums import (
    TRUE_FALSE_CHOICES, DELIVERY_REQUIRED_CHOICES, birth_years, operational_years, get_service_hours,
    current_year, get_exp_year_choices, get_exp_month_choices, get_vehicle_choices, get_extra_miles_choices
)
from marketing.models import NewsItem


class CSSClassMixin:

    def add_widget_css_class(self, field, css_class_name):
        widget_css_class = self.fields[field].widget.attrs.get('class')
        widget_css_classes = widget_css_class.split(' ') if widget_css_class else []
        widget_css_classes.append(css_class_name)
        css_class_string = ' '.join(list(set(widget_css_classes)))
        self.fields[field].widget.attrs['class'] = css_class_string

    def style_customer_search_fields(self):
        # Populate conditionally non-editable fields from linked customer
        phone_fields = ['home_phone', 'work_phone', 'mobile_phone']
        for field in ['first_name', 'last_name', 'email', 'home_phone', 'work_phone', 'mobile_phone']:
            field_classes = ['newuserfield']
            if self.instance.id:
                field_classes.append('dont-edit')
            if field in phone_fields:
                field_classes.append('phone')
                field_classes.append('short')
            field_classes_str = ' '.join(field_classes)
            self.fields[field].widget.attrs['class'] = field_classes_str
            if self.instance.customer:
                if field in phone_fields:
                    try:
                        self.fields[field].initial = getattr(self.instance.customer, field).as_national
                    except AttributeError:
                        pass
                else:
                    self.fields[field].initial = getattr(self.instance.customer, field, None) or getattr(self.instance.customer.user, field, None)


# TODO: Add slug to the visible form fields and set on both models

class VehicleForm(CSSClassMixin, forms.ModelForm):
    external_owner = forms.ModelChoiceField(queryset=Consigner.objects.all(), empty_label='PRI', required=False)
    toll_tag = forms.ModelChoiceField(queryset=TollTag.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.add_widget_css_class('policy_phone', 'phone')

        for field in [
            'year', 'plate', 'mileage',
        ]:
            self.add_widget_css_class(field, 'short')

        self.fields['toll_tag'].initial = TollTag.objects.filter(vehicle=self.instance).first()

    class Meta:
        model = Vehicle
        exclude = ('slug', 'vehicle_marketing_id',)


class VehicleMarketingForm(CSSClassMixin, forms.ModelForm):

    WEIGHTING_CHOICES = (
        (0, '0 - Normal'),
        (1, '+1'),
        (2, '+2'),
        (3, '+3'),
    )

    tight_fit = forms.TypedChoiceField(coerce=lambda x: x == 'True', initial=False, choices=TRUE_FALSE_CHOICES)
    weighting = forms.ChoiceField(choices=WEIGHTING_CHOICES)

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
    tax_percent = forms.DecimalField(disabled=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['vehicle'].choices = get_vehicle_choices()
        self.fields['vehicle'].widget.attrs['class'] = 'check-conflict'

        self.style_customer_search_fields()

        self.init_reservation_date_time()

        for field in ['drivers', 'delivery_zip', 'tax_percent', 'miles_included', 'coupon_code']:
            self.add_widget_css_class(field, 'short')

        # self.fields['tax_percent'].initial = decimal.Decimal(settings.DEFAULT_TAX_RATE) * 100
        self.fields['tax_percent'].initial = self.instance.get_price_data()['tax_rate'] * 100
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
    tax_percent = forms.DecimalField(disabled=True)

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

        self.fields['tax_percent'].initial = self.instance.get_price_data()['tax_rate'] * 100
        self.fields['override_subtotal'].widget.attrs['placeholder'] = 'Override'

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.user:
            self.fields['clone_email'].initial = self.instance.user.next_disambiguated_email

    def clean_clone_email(self):
        email = self.cleaned_data['clone_email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(f'A user with email {email} already exists.')
        return email

    def clean(self):
        return super().clean()

    class Meta:
        model = Customer
        fields = ('clone_first_name', 'clone_last_name', 'clone_email', 'clone_duplicate_license',)


class CouponForm(forms.ModelForm):

    class Meta:
        model = Coupon
        fields = '__all__'


class TollTagForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['vehicle'].choices = get_vehicle_choices(allow_null=True)

    class Meta:
        model = TollTag
        fields = '__all__'


class TaxRateForm(CSSClassMixin, forms.ModelForm):
    total_rate_as_percent = forms.DecimalField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['total_rate_as_percent'].initial = self.instance.total_rate_as_percent
        for field in ['postal_code', 'total_rate_as_percent']:
            self.add_widget_css_class(field, 'short')

    class Meta:
        model = TaxRate
        # fields = '__all__'
        exclude = ('country', 'total_rate',)


# class GuidedDriveForm(forms.ModelForm):
#     class Meta:
#         model = GuidedDrive
#         fields = '__all__'


class GuidedDriveForm(CSSClassMixin, forms.ModelForm):

    requested_date_picker = forms.DateField(required=False)
    backup_date_picker = forms.DateField(required=False)
    customer = forms.ModelChoiceField(queryset=Customer.objects.all(), widget=forms.HiddenInput())
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    email = forms.EmailField(required=False)
    home_phone = PhoneNumberField(required=False)
    work_phone = PhoneNumberField(required=False)
    mobile_phone = PhoneNumberField(required=False)
    big_and_tall = forms.TypedChoiceField(coerce=lambda x: x == 'True', initial=False, choices=TRUE_FALSE_CHOICES)
    customer_notes = forms.CharField(widget=forms.Textarea(attrs={'class': 'customer-notes'}), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['vehicle_choice_1'].choices = get_vehicle_choices(allow_null=True)
        self.fields['vehicle_choice_2'].choices = get_vehicle_choices(allow_null=True)
        self.fields['vehicle_choice_3'].choices = get_vehicle_choices(allow_null=True)
        if self.instance.requested_date:
            self.fields['requested_date_picker'].initial = self.instance.requested_date.strftime('%m/%d/%Y')
        if self.instance.backup_date:
            self.fields['backup_date_picker'].initial = self.instance.backup_date.strftime('%m/%d/%Y')
        self.fields['override_subtotal'].widget.attrs['placeholder'] = 'Override'

        short_fields = [
            'requested_date_picker', 'backup_date_picker', 'num_drivers', 'num_passengers', 'num_minors', 'coupon_code'
        ]
        for field in short_fields:
            try:
                self.add_widget_css_class(field, 'short')
            except KeyError:
                pass

        self.style_customer_search_fields()

    def clean(self):
        super().clean()
        self.cleaned_data['requested_date'] = self.cleaned_data['requested_date_picker']
        self.cleaned_data['backup_date'] = self.cleaned_data['backup_date_picker']


class JoyRideForm(GuidedDriveForm):

    class Meta:
        model = JoyRide
        # fields = '__all__'
        exclude = ('confirmation_code',)


class PerformanceExperienceForm(GuidedDriveForm):

    class Meta:
        model = PerformanceExperience
        # fields = '__all__'
        exclude = ('confirmation_code',)


class ConsignerForm(forms.ModelForm):

    class Meta:
        model = Consigner
        fields = '__all__'
        # exclude = ('confirmation_code',)


class ConsignmentPaymentForm(CSSClassMixin, forms.ModelForm):

    paid_on_picker = forms.DateField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.paid_at:
            self.fields['paid_on_picker'].initial = self.instance.paid_at.strftime('%m/%d/%Y')

        short_fields = [
            'amount', 'paid_on_picker'
        ]
        for field in short_fields:
            self.add_widget_css_class(field, 'short')

    def clean(self):
        super().clean()
        self.cleaned_data['paid_at'] = self.cleaned_data['paid_on_picker']

    class Meta:
        model = ConsignmentPayment
        fields = '__all__'
        # exclude = ('confirmation_code',)


class NewsItemForm(forms.ModelForm):

    class Meta:
        model = NewsItem
        fields = '__all__'
        # exclude = ('confirmation_code',)


class GiftCertificateForm(forms.ModelForm):
    is_paid = forms.TypedChoiceField(coerce=lambda x: x == 'True', initial=False, choices=TRUE_FALSE_CHOICES)
    is_used = forms.TypedChoiceField(coerce=lambda x: x == 'True', initial=False, choices=TRUE_FALSE_CHOICES)
    cc_exp_yr = forms.ChoiceField(choices=get_exp_year_choices(since_founding=True, allow_null=False))
    cc_exp_mo = forms.ChoiceField(choices=get_exp_month_choices(allow_null=False))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['cc_number'].widget.attrs['class'] = 'cc-field'

    class Meta:
        model = GiftCertificate
        # fields = '__all__'
        exclude = ('tag',)
