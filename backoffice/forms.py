import datetime
import pytz
import decimal

from django.conf import settings
from django import forms
from phonenumber_field.formfields import PhoneNumberField

from fleet.models import Vehicle, VehicleMarketing, VehiclePicture, VehicleVideo, TollTag
from consignment.models import Consigner, ConsignmentPayment
from users.models import User, Employee, Customer
from sales.models import (
    Reservation, Rental, GuidedDrive, JoyRide, PerformanceExperience, Coupon, TaxRate, GiftCertificate, AdHocPayment,
    Charge, Card, RedFlag
)
from sales.enums import (
    TRUE_FALSE_CHOICES, DELIVERY_REQUIRED_CHOICES, birth_years, operational_years, get_service_hours,
    current_year, get_exp_year_choices, get_exp_month_choices, get_vehicle_choices, get_extra_miles_choices
)
from marketing.models import NewsItem, SiteContent, EmailImage
from service.models import Damage, ScheduledService, IncidentalService
from marketing.utils import RECIPIENT_CLASS_METHOD_MAP, RECIPIENT_CLASS_LABEL_MAP


class CSSClassMixin:

    def add_widget_css_class(self, field, css_class_name):
        widget_css_class = self.fields[field].widget.attrs.get('class')
        widget_css_classes = widget_css_class.split(' ') if widget_css_class else []
        widget_css_classes.append(css_class_name)
        css_class_string = ' '.join(list(set(widget_css_classes)))
        self.fields[field].widget.attrs['class'] = css_class_string


class CustomerSearchMixin:

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

    tight_fit = forms.ChoiceField(choices=TRUE_FALSE_CHOICES, initial=False)
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


class ReservationForm(ReservationDateTimeMixin, CSSClassMixin, CustomerSearchMixin, forms.ModelForm):

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
        if self.instance.id:
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
        return email

    class Meta:
        model = Employee
        # fields = '__all__'
        exclude = ('user',)


class CardForm(CSSClassMixin, forms.ModelForm):

    cc_fields = ['number']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.cc_fields:
            self.fields[field].widget.attrs['class'] = 'cc-field'

    class Meta:
        model = Card
        fields = ('number', 'exp_year', 'exp_month', 'cvv',)
        # exclude = ('user', 'rentals_count',)


class CustomerForm(CSSClassMixin, forms.ModelForm):

    email = forms.EmailField(required=True)
    receive_email = forms.ChoiceField(choices=TRUE_FALSE_CHOICES, initial=False)

    cc_number = forms.CharField(required=False)
    cc_exp_yr = forms.ChoiceField(choices=get_exp_year_choices(since_founding=True, allow_null=False))
    cc_exp_mo = forms.ChoiceField(choices=get_exp_month_choices(allow_null=False))
    cc_cvv = forms.CharField(required=False)
    cc_phone = PhoneNumberField(region='US', required=False)

    cc2_number = forms.CharField(required=False)
    cc2_exp_yr = forms.ChoiceField(choices=get_exp_year_choices(since_founding=True, allow_null=True), required=False)
    cc2_exp_mo = forms.ChoiceField(choices=get_exp_month_choices(allow_null=True), required=False)
    cc2_cvv = forms.CharField(required=False)
    cc2_phone = PhoneNumberField(region='US', required=False)

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
            'zip', 'fax', 'insurance_company_phone', 'discount_pct',
            'cc_cvv', 'cc_phone', 'cc2_cvv', 'cc2_phone',
        ]
        for field in short_fields:
            self.add_widget_css_class(field, 'short')

        # Set initial values on CC fields from linked Card models
        if self.instance.card_1:
            self.fields['cc_number'].initial = self.instance.card_1.number
            self.fields['cc_exp_yr'].initial = self.instance.card_1.exp_year
            self.fields['cc_exp_mo'].initial = self.instance.card_1.exp_month
            self.fields['cc_cvv'].initial = self.instance.card_1.cvv
            self.fields['cc_phone'].initial = self.instance.card_1.phone

        if self.instance.card_2:
            self.fields['cc2_number'].initial = self.instance.card_2.number
            self.fields['cc2_exp_yr'].initial = self.instance.card_2.exp_year
            self.fields['cc2_exp_mo'].initial = self.instance.card_2.exp_month
            self.fields['cc2_cvv'].initial = self.instance.card_2.cvv
            self.fields['cc2_phone'].initial = self.instance.card_2.phone

    # def get_exp_year_choices(self):
    #     return ((year, year) for year in range(settings.COMPANY_FOUNDING_YEAR, current_year + 11))

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exclude(pk=self.instance.user.id).exists():
            raise forms.ValidationError(f'A user with email {email} already exists.')
        return email

    class Meta:
        model = Customer
        # fields = '__all__'
        exclude = ('user', 'rentals_count', 'stripe_customer',)


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


class AdHocPaymentForm(forms.ModelForm):
    is_paid = forms.ChoiceField(choices=TRUE_FALSE_CHOICES, initial=False)
    is_submitted = forms.ChoiceField(choices=TRUE_FALSE_CHOICES, initial=False)

    cc_number = forms.CharField(required=False)
    cc_exp_yr = forms.ChoiceField(choices=get_exp_year_choices(since_founding=True, allow_null=False))
    cc_exp_mo = forms.ChoiceField(choices=get_exp_month_choices(allow_null=False))
    cc_cvv = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['cc_number'].widget.attrs['class'] = 'cc-field'

        # Set initial values on CC fields from linked Card models
        if self.instance.card:
            self.fields['cc_number'].initial = self.instance.card.number
            self.fields['cc_exp_yr'].initial = self.instance.card.exp_year
            self.fields['cc_exp_mo'].initial = self.instance.card.exp_month
            self.fields['cc_cvv'].initial = self.instance.card.cvv

    class Meta:
        model = AdHocPayment
        # fields = '__all__'
        exclude = ('submitted_at', 'is_submitted', 'paid_at', 'is_paid', 'card',)


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


class GuidedDriveForm(CSSClassMixin, CustomerSearchMixin, forms.ModelForm):

    requested_date_picker = forms.DateField(required=False)
    backup_date_picker = forms.DateField(required=False)
    customer = forms.ModelChoiceField(queryset=Customer.objects.all(), widget=forms.HiddenInput())
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    email = forms.EmailField(required=False)
    home_phone = PhoneNumberField(required=False)
    work_phone = PhoneNumberField(required=False)
    mobile_phone = PhoneNumberField(required=False)
    big_and_tall = forms.ChoiceField(choices=TRUE_FALSE_CHOICES, initial=False)
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
        # fields = '__all__'
        exclude = ('slug',)


class SiteContentForm(forms.ModelForm):

    class Meta:
        model = SiteContent
        # fields = '__all__'
        exclude = ('page', 'name',)


class GiftCertificateForm(forms.ModelForm):
    is_paid = forms.ChoiceField(choices=TRUE_FALSE_CHOICES, initial=False)
    is_used = forms.ChoiceField(choices=TRUE_FALSE_CHOICES, initial=False)

    cc_name = forms.CharField(required=False)
    cc_number = forms.CharField(required=False)
    cc_exp_yr = forms.ChoiceField(choices=get_exp_year_choices(since_founding=True, allow_null=False))
    cc_exp_mo = forms.ChoiceField(choices=get_exp_month_choices(allow_null=False))
    cc_cvv = forms.CharField(required=False)
    cc_phone = PhoneNumberField(region='US', required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['cc_number'].widget.attrs['class'] = 'cc-field'

        # Set initial values on CC fields from linked Card models
        if self.instance.card:
            self.fields['cc_name'].initial = self.instance.card.name
            self.fields['cc_number'].initial = self.instance.card.number
            self.fields['cc_exp_yr'].initial = self.instance.card.exp_year
            self.fields['cc_exp_mo'].initial = self.instance.card.exp_month
            self.fields['cc_cvv'].initial = self.instance.card.cvv
            self.fields['cc_phone'].initial = self.instance.card.phone

    class Meta:
        model = GiftCertificate
        # fields = '__all__'
        exclude = ('tag', 'card',)


class StripeChargeForm(forms.ModelForm):

    CHARGE_TYPE_CHOICES = (
        (True, 'Charge'),
        (False, 'Auth only'),
    )

    charge_type = forms.ChoiceField(choices=CHARGE_TYPE_CHOICES, initial=False)
    cc_exp_yr = forms.ChoiceField(choices=get_exp_year_choices(since_founding=True, allow_null=False))
    cc_exp_mo = forms.ChoiceField(choices=get_exp_month_choices(allow_null=False))
    stripe_token = forms.CharField(widget=forms.HiddenInput(), required=False)
    stripe_error = forms.CharField(widget=forms.HiddenInput(), required=False)
    stripe_error_param = forms.CharField(widget=forms.HiddenInput(), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['phone'].widget.attrs['class'] = 'phone'
        self.fields['cc_number'].widget.attrs['class'] = 'cc-field'
        short_fields = [
            'zip', 'home_phone', 'mobile_phone', 'work_phone', 'fax', 'insurance_company_phone', 'discount_pct',
            'cc_cvv', 'cc_phone', 'cc2_cvv', 'cc2_phone',
        ]
        # for field in short_fields:
        #     self.add_widget_css_class(field, 'short')

        # Set initial values on CC fields from linked Card models
        if self.instance.card:
            self.fields['cc_number'].initial = self.instance.card.number
            self.fields['cc_exp_yr'].initial = self.instance.card.exp_year
            self.fields['cc_exp_mo'].initial = self.instance.card.exp_month
            self.fields['cc_cvv'].initial = self.instance.card.cvv

    # def clean_stripe_token(self):
    #     if self.cleaned_data['stripe_error']:
    #         raise forms.ValidationError(self.cleaned_data['stripe_error'])

    def clean(self):
        if self.cleaned_data['stripe_error']:
            raise forms.ValidationError(self.cleaned_data['stripe_error'])

    class Meta:
        model = Charge
        # fields = '__all__'
        exclude = ('uuid', 'card',)


class CardForm(forms.ModelForm):

    class Meta:
        model = Card
        fields = '__all__'
        # exclude = ('uuid',)


class RedFlagForm(forms.ModelForm):

    class Meta:
        model = RedFlag
        fields = '__all__'
        # exclude = ('confirmation_code',)


class DamageForm(CSSClassMixin, forms.ModelForm):

    damaged_on = forms.DateField(widget=forms.DateInput(), required=False)
    repaired_on = forms.DateField(widget=forms.DateInput(), required=False)
    is_repaired = forms.ChoiceField(choices=TRUE_FALSE_CHOICES, initial=False)
    is_paid = forms.ChoiceField(choices=TRUE_FALSE_CHOICES, initial=False)
    in_house_repair = forms.ChoiceField(choices=TRUE_FALSE_CHOICES, initial=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['vehicle'].choices = get_vehicle_choices()
        if self.instance.damaged_at:
            damaged_at_localized = self.instance.damaged_at.astimezone(pytz.timezone(settings.TIME_ZONE))
            self.fields['damaged_on'].initial = damaged_at_localized.strftime('%m/%d/%Y')
        if self.instance.repaired_at:
            repaired_at_localized = self.instance.repaired_at.astimezone(pytz.timezone(settings.TIME_ZONE))
            self.fields['repaired_on'].initial = repaired_at_localized.strftime('%m/%d/%Y')

        short_fields = [
            'damaged_on', 'repaired_on', 'cost', 'customer_billed_amount', 'customer_paid_amount',
        ]
        for field in short_fields:
            self.add_widget_css_class(field, 'short')

    def clean(self):
        super().clean()
        self.cleaned_data['damaged_at'] = self.cleaned_data['damaged_on']
        self.cleaned_data['repaired_at'] = self.cleaned_data['repaired_on']

    class Meta:
        model = Damage
        fields = '__all__'
        # exclude = ('confirmation_code',)


class ScheduledServiceForm(CSSClassMixin, forms.ModelForm):

    done_on = forms.DateField(widget=forms.DateInput(), required=False)
    next_on = forms.DateField(widget=forms.DateInput(), required=False)
    is_due = forms.ChoiceField(choices=TRUE_FALSE_CHOICES, initial=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['vehicle'].choices = get_vehicle_choices()
        if self.instance.done_at:
            done_at_localized = self.instance.done_at.astimezone(pytz.timezone(settings.TIME_ZONE))
            self.fields['done_on'].initial = done_at_localized.strftime('%m/%d/%Y')
        if self.instance.next_at:
            next_at_localized = self.instance.next_at.astimezone(pytz.timezone(settings.TIME_ZONE))
            self.fields['next_on'].initial = next_at_localized.strftime('%m/%d/%Y')

        short_fields = [
            'done_on', 'done_mileage', 'next_on', 'next_mileage',
        ]
        for field in short_fields:
            self.add_widget_css_class(field, 'short')

    def clean(self):
        super().clean()
        self.cleaned_data['done_at'] = self.cleaned_data['done_on']
        self.cleaned_data['next_at'] = self.cleaned_data['next_on']

    class Meta:
        model = ScheduledService
        fields = '__all__'
        # exclude = ('confirmation_code',)


class IncidentalServiceForm(CSSClassMixin, forms.ModelForm):

    done_on = forms.DateField(widget=forms.DateInput(), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['vehicle'].choices = get_vehicle_choices()
        if self.instance.done_at:
            done_at_localized = self.instance.done_at.astimezone(pytz.timezone(settings.TIME_ZONE))
            self.fields['done_on'].initial = done_at_localized.strftime('%m/%d/%Y')

        short_fields = [
            'done_on', 'mileage',
        ]
        for field in short_fields:
            self.add_widget_css_class(field, 'short')

    def clean(self):
        super().clean()
        self.cleaned_data['done_at'] = self.cleaned_data['done_on']

    class Meta:
        model = IncidentalService
        fields = '__all__'
        # exclude = ('confirmation_code',)


class VehicleSelectorForm(forms.Form):
    select_vehicle = forms.ChoiceField(choices=get_vehicle_choices(allow_null=True, null_display_value='(Select vehicle)'))


class MassEmailForm(forms.Form):
    send_to = forms.ChoiceField()
    subject = forms.CharField()
    body = forms.CharField(widget=forms.Textarea(), required=False)
    preview = forms.BooleanField(widget=forms.HiddenInput(), initial=True, required=False)
    include_header = forms.ChoiceField(choices=TRUE_FALSE_CHOICES, initial=True, required=False)
    # include_header = forms.BooleanField(initial=True, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Calculate all the counts of potential recipient classes
        recipient_counts = {k: RECIPIENT_CLASS_METHOD_MAP[k]().count() for k in RECIPIENT_CLASS_LABEL_MAP.keys()}

        # Create labels combining static text with the calculated counts
        self.combined_labels = {key: f'{value} ({recipient_counts[key]})' for key, value in RECIPIENT_CLASS_LABEL_MAP.items()}

        # Populate the recipient dropdown choices using centralized key names we can use to send out the
        # actual emails later in the form_valid method in the view
        send_to_choices = list((k, v) for k, v in self.combined_labels.items())
        self.fields['send_to'].choices = send_to_choices

    def clean(self):
        self.recipient_label =  self.combined_labels[self.cleaned_data['send_to']]


class EmailImageForm(forms.ModelForm):

    def clean(self):
        super().clean()

    class Meta:
        model = EmailImage
        fields = '__all__'
        # exclude = ('confirmation_code',)
