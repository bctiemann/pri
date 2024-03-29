import datetime
import pytz
import imghdr
import decimal
import ipaddress
import logging

from django.conf import settings
from django import forms
from phonenumber_field.formfields import PhoneNumberField
from localflavor.us.forms import USZipCodeField

from fleet.models import Vehicle, VehicleMarketing, VehiclePicture, VehicleVideo, TollTag
from consignment.models import Consigner, ConsignmentPayment
from users.models import User, Employee, Customer
from sales.models import (
    Reservation, Rental, GuidedDrive, JoyRide, PerformanceExperience, Coupon, TaxRate, GiftCertificate, AdHocPayment,
    Charge, Card, RedFlag, IPBan
)
from sales.enums import (
    TRUE_FALSE_CHOICES, DELIVERY_REQUIRED_CHOICES, birth_years, operational_years, get_service_hours,
    current_year, get_exp_year_choices, get_exp_month_choices, get_vehicle_choices, get_extra_miles_choices
)
from marketing.models import NewsItem, SiteContent, EmailImage
from service.models import Damage, ScheduledService, IncidentalService
from marketing.utils import RECIPIENT_CLASS_METHOD_MAP, RECIPIENT_CLASS_LABEL_MAP

logger = logging.getLogger(__name__)


# This mixin provides a method for adding CSS classes to arbitrary form fields. Also a form class can define a tuple or
# list of cc_fields, phone_fields, or short_fields and they will automatically be given "cc-field", "phone", and "short"
# classes accordingly.
class CSSClassMixin:
    cc_fields = ()
    phone_fields = ()
    short_fields = ()
    ssn_fields = ()

    def add_widget_css_class(self, field, css_class_name):
        if not self.fields.get(field):
            return
        widget_css_class = self.fields[field].widget.attrs.get('class')
        widget_css_classes = widget_css_class.split(' ') if widget_css_class else []
        widget_css_classes.append(css_class_name)
        css_class_string = ' '.join(list(set(widget_css_classes)))
        self.fields[field].widget.attrs['class'] = css_class_string

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.cc_fields:
            self.add_widget_css_class(field, 'cc-field')
        for field in self.phone_fields:
            self.add_widget_css_class(field, 'phone')
        for field in self.short_fields:
            self.add_widget_css_class(field, 'short')
        for field in self.ssn_fields:
            self.add_widget_css_class(field, 'ssn')


# Provides styling and initial value formatting for the customer search fields in Reservation etc. forms.
class CustomerSearchMixin:

    def style_customer_search_fields(self):
        # Populate conditionally non-editable fields from linked customer
        phone_fields = ['home_phone', 'work_phone', 'mobile_phone']
        for field in ['first_name', 'last_name', 'email', 'home_phone', 'work_phone', 'mobile_phone']:
            field_classes = ['newuserfield']
            if self.instance.id or self.initial.get('customer'):
                field_classes.append('dont-edit')
            if field in phone_fields:
                field_classes.append('phone')
                field_classes.append('short')
            field_classes_str = ' '.join(field_classes)
            self.fields[field].widget.attrs['class'] = field_classes_str
            customer = self.instance.customer or self.initial.get('customer')
            if customer:
                if field in phone_fields:
                    try:
                        self.fields[field].initial = getattr(customer, field).as_national
                    except AttributeError:
                        pass
                else:
                    self.fields[field].initial = getattr(customer, field, None) or getattr(customer.user, field, None)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.style_customer_search_fields()


# TODO: Add slug to the visible form fields and set on both models

class VehicleForm(CSSClassMixin, forms.ModelForm):
    phone_fields = ('policy_phone',)
    short_fields = ('year', 'plate', 'mileage',)

    make = forms.CharField(required=True)
    model = forms.CharField(required=True)
    year = forms.IntegerField(required=True)
    external_owner = forms.ModelChoiceField(queryset=Consigner.objects.all(), empty_label='PRI', required=False)
    toll_tag = forms.ModelChoiceField(queryset=TollTag.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # self.add_widget_css_class('policy_phone', 'phone')
        #
        # for field in [
        #     'year', 'plate', 'mileage',
        # ]:
        #     self.add_widget_css_class(field, 'short')

        self.fields['toll_tag'].initial = TollTag.objects.filter(vehicle=self.instance).first()

    class Meta:
        model = Vehicle
        exclude = ('slug', 'vehicle_marketing_id',)


class VehicleMarketingForm(CSSClassMixin, forms.ModelForm):
    short_fields = (
        'horsepower', 'torque', 'top_speed', 'gears', 'price_per_day',
        'discount_2_day', 'discount_3_day', 'discount_7_day', 'security_deposit', 'miles_included',
    )

    WEIGHTING_CHOICES = (
        (0, '0 - Normal'),
        (1, '+1'),
        (2, '+2'),
        (3, '+3'),
    )

    tight_fit = forms.ChoiceField(choices=TRUE_FALSE_CHOICES, initial=False)
    weighting = forms.ChoiceField(choices=WEIGHTING_CHOICES)

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #
    #     for field in [
    #         'horsepower', 'torque', 'top_speed', 'gears', 'price_per_day',
    #         'discount_2_day', 'discount_3_day', 'discount_7_day', 'security_deposit', 'miles_included',
    #     ]:
    #         self.add_widget_css_class(field, 'short')

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

    ALLOWED_IMAGE_FORMATS = ['jpg', 'jpeg', 'png']

    def clean_image(self):
        if not self.cleaned_data.get('image'):
            error_message = 'No image uploaded.'
            logger.info(error_message)
            raise forms.ValidationError(error_message)

        image_ext = imghdr.what(self.cleaned_data['image'])
        if image_ext not in self.ALLOWED_IMAGE_FORMATS:
            allowed_formats = ', '.join(self.ALLOWED_IMAGE_FORMATS)
            error_message = f'Image format {image_ext} not allowed. Only {allowed_formats} allowed.'
            logger.info(error_message)
            raise forms.ValidationError(error_message)

        return self.cleaned_data['image']

    class Meta:
        model = VehiclePicture
        fields = ('image',)


class VehicleVideoForm(forms.ModelForm):

    # TODO: validate video and thumbnail (prevent saving if nothing uploaded)

    class Meta:
        model = VehicleVideo
        fields = ('video_mp4', 'video_webm', 'poster', 'thumbnail', 'length', 'title', 'blurb',)


# Because the model fields are out_at and back_at, but we want to provide split date/time widgets for picking the
# out_date and out_time separately, we provide these additional fields and clean() and init() methods for handling them
# in Reservation and Rental forms.
class ReservationDateTimeMixin(forms.ModelForm):

    out_at_date = forms.DateField(widget=forms.DateInput(attrs={'class': 'short check-conflict'}))
    out_at_time = forms.ChoiceField(choices=get_service_hours(), widget=forms.Select(attrs={'class': 'check-conflict'}))
    back_at_date = forms.DateField(widget=forms.DateInput(attrs={'class': 'short check-conflict'}))
    back_at_time = forms.ChoiceField(choices=get_service_hours(), widget=forms.Select(attrs={'class': 'check-conflict'}))

    def init_reservation_date_time(self):
        if self.instance.out_at and self.instance.back_at:
            out_at_localized = self.instance.out_at.astimezone(pytz.timezone(settings.TIME_ZONE))
            back_at_localized = self.instance.back_at.astimezone(pytz.timezone(settings.TIME_ZONE))
            self.fields['out_at_date'].initial = out_at_localized.strftime(settings.DATE_FORMAT_INPUT)
            self.fields['back_at_date'].initial = back_at_localized.strftime(settings.DATE_FORMAT_INPUT)
            self.fields['out_at_time'].initial = out_at_localized.strftime(settings.TIME_FORMAT_INPUT)
            self.fields['back_at_time'].initial = back_at_localized.strftime(settings.TIME_FORMAT_INPUT)

    def clean(self):
        super().clean()
        out_at_time = datetime.datetime.strptime(self.cleaned_data['out_at_time'], settings.TIME_FORMAT_INPUT).time()
        back_at_time = datetime.datetime.strptime(self.cleaned_data['back_at_time'], settings.TIME_FORMAT_INPUT).time()
        self.cleaned_data['out_at'] = datetime.datetime.combine(
            self.cleaned_data['out_at_date'],
            out_at_time,
        ).astimezone(pytz.timezone(settings.TIME_ZONE))
        self.cleaned_data['back_at'] = datetime.datetime.combine(
            self.cleaned_data['back_at_date'],
            back_at_time,
        ).astimezone(pytz.timezone(settings.TIME_ZONE))


class ReservationForm(ReservationDateTimeMixin, CSSClassMixin, CustomerSearchMixin, forms.ModelForm):
    short_fields = ('drivers', 'delivery_zip', 'tax_percent', 'miles_included', 'coupon_code',)

    customer = forms.ModelChoiceField(queryset=Customer.objects.all(), widget=forms.HiddenInput())
    reservation = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    email = forms.EmailField(required=False)
    home_phone = PhoneNumberField(required=False)
    work_phone = PhoneNumberField(required=False)
    mobile_phone = PhoneNumberField(required=False)

    delivery_required = forms.TypedChoiceField(coerce=lambda x: x == 'True', choices=DELIVERY_REQUIRED_CHOICES)
    extra_miles = forms.ChoiceField(choices=get_extra_miles_choices())
    send_email = forms.TypedChoiceField(coerce=lambda x: x == 'True', choices=TRUE_FALSE_CHOICES, required=False)
    is_military = forms.TypedChoiceField(coerce=lambda x: x == 'True', initial=False, choices=TRUE_FALSE_CHOICES, required=False)
    customer_notes = forms.CharField(widget=forms.Textarea(attrs={'class': 'customer-notes'}), required=False)
    tax_percent = forms.DecimalField(disabled=True, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['vehicle'].choices = get_vehicle_choices()
        self.fields['vehicle'].widget.attrs['class'] = 'check-conflict'

        self.init_reservation_date_time()

        if self.instance.id:
            self.fields['tax_percent'].initial = self.instance.get_price_data()['tax_rate'] * 100
            self.fields['override_subtotal'].widget.attrs['placeholder'] = 'Override'

        if self.initial.get('customer'):
            customer = self.initial['customer']
            if isinstance(customer, Customer):
                self.fields['first_name'].initial = customer.first_name
                self.fields['last_name'].initial = customer.last_name
                self.fields['email'].initial = customer.email

    def clean(self):
        super().clean()
        vehicle_marketing = self.cleaned_data['vehicle'].vehicle_marketing
        self.cleaned_data['miles_included'] = vehicle_marketing.miles_included
        self.cleaned_data['deposit_amount'] = vehicle_marketing.security_deposit

        if self.cleaned_data['back_at'] < self.cleaned_data['out_at']:
            raise forms.ValidationError('Return date/time is earlier than out date/time.')

    class Meta:
        model = Reservation
        # fields = '__all__'
        exclude = ('confirmation_code',)


class ReservationCreateForm(ReservationForm):

    customer = forms.ModelChoiceField(queryset=Customer.objects.all(), widget=forms.HiddenInput(), required=False)
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()

    def clean(self):
        super().clean()
        customer = self.cleaned_data.get('customer')
        email = self.cleaned_data.get('email')
        if not customer and email:
            customer = Customer.objects.filter(user__email=email).first()
        if not customer and User.objects.filter(email=self.cleaned_data['email'], customer__isnull=True).exists():
            raise forms.ValidationError('User with the specified email (but no Customer) already exists.')
        self.cleaned_data['customer'] = customer

    class Meta:
        model = Reservation
        fields = (
            'customer', 'first_name', 'last_name', 'email', 'mobile_phone', 'work_phone', 'home_phone',
            'vehicle', 'out_at', 'out_at_date', 'out_at_time', 'back_at', 'back_at_date', 'back_at_time',
            'drivers', 'status', 'delivery_required','delivery_zip', 'coupon_code', 'extra_miles', 'miles_included',
            'deposit_amount', 'customer_notes',
        )
        # fields = '__all__'
        # exclude = ('confirmation_code', 'customer',)


class RentalForm(ReservationDateTimeMixin, CSSClassMixin, forms.ModelForm):
    short_fields = (
        'delivery_zip', 'miles_included', 'mileage_out', 'mileage_back', 'coupon_code',
        'deposit_amount', 'deposit_charged_on', 'deposit_refund_amount', 'deposit_refunded_on',
        'rental_discount_pct', 'tax_percent'
    )

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

        self.fields['tax_percent'].initial = self.instance.get_price_data()['tax_rate'] * 100
        self.fields['override_subtotal'].widget.attrs['placeholder'] = 'Override'

        self.init_reservation_date_time()
        if self.instance.deposit_charged_at:
            deposit_charged_at_localized = self.instance.deposit_charged_at.astimezone(pytz.timezone(settings.TIME_ZONE))
            self.fields['deposit_charged_on'].initial = deposit_charged_at_localized.strftime(settings.DATE_FORMAT_INPUT)
        if self.instance.deposit_refunded_at:
            deposit_refunded_at_localized = self.instance.deposit_refunded_at.astimezone(pytz.timezone(settings.TIME_ZONE))
            self.fields['deposit_refunded_on'].initial = deposit_refunded_at_localized.strftime(settings.DATE_FORMAT_INPUT)

    def clean(self):
        super().clean()
        self.cleaned_data['deposit_charged_at'] = self.cleaned_data['deposit_charged_on']
        self.cleaned_data['deposit_refunded_at'] = self.cleaned_data['deposit_refunded_on']

    class Meta:
        model = Rental
        exclude = ('confirmation_code', 'customer', 'back_at_orig',)


class RentalConversionForm(forms.ModelForm):

    class Meta:
        model = Rental
        exclude = ()


class EmployeeForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput(), required=True)
    date_of_birth = forms.DateField(widget=forms.SelectDateWidget(years=birth_years))

    def clean_email(self):
        email = self.cleaned_data['email']
        matching_users = User.objects.filter(email=email)
        if self.instance.id:
            matching_users = matching_users.exclude(pk=self.instance.user.id)
        if matching_users.exists():
            raise forms.ValidationError(f'A user with email {email} already exists.')
        return email

    class Meta:
        model = Employee
        # fields = '__all__'
        exclude = ('user',)


class CardForm(CSSClassMixin, forms.ModelForm):
    cc_fields = ('number',)

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     for field in self.cc_fields:
    #         self.fields[field].widget.attrs['class'] = 'cc-field'

    class Meta:
        model = Card
        fields = ('number', 'exp_year', 'exp_month', 'cvv',)
        # exclude = ('user', 'rentals_count',)


class CustomerForm(CSSClassMixin, forms.ModelForm):
    cc_fields = ('cc_number', 'cc2_number',)
    phone_fields = ('home_phone', 'work_phone', 'mobile_phone', 'fax', 'insurance_company_phone', 'cc_phone', 'cc2_phone',)
    short_fields = ('zip', 'fax', 'insurance_company_phone', 'discount_pct', 'cc_cvv', 'cc_phone', 'cc2_cvv', 'cc2_phone',)

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
        # phone_fields = ['home_phone', 'work_phone', 'mobile_phone', 'fax', 'insurance_company_phone', 'cc_phone', 'cc2_phone']
        # for field in phone_fields:
        #     self.fields[field].widget.attrs['class'] = 'phone'
        # cc_fields = ['cc_number', 'cc2_number']
        # for field in cc_fields:
        #     self.fields[field].widget.attrs['class'] = 'cc-field'
        # short_fields = [
        #     'zip', 'fax', 'insurance_company_phone', 'discount_pct',
        #     'cc_cvv', 'cc_phone', 'cc2_cvv', 'cc2_phone',
        # ]
        # for field in short_fields:
        #     self.add_widget_css_class(field, 'short')

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
        exclude = ('user', 'rentals_count', 'stripe_customer', 'card_1_status', 'card_2_status',)


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


class CouponForm(CSSClassMixin, forms.ModelForm):
    short_fields = ('percent',)

    class Meta:
        model = Coupon
        fields = '__all__'


class AdHocPaymentForm(CSSClassMixin, forms.ModelForm):
    cc_fields = ('cc_number',)
    phone_fields = ('phone',)

    is_paid = forms.ChoiceField(choices=TRUE_FALSE_CHOICES, initial=False)
    is_submitted = forms.ChoiceField(choices=TRUE_FALSE_CHOICES, initial=False)

    cc_number = forms.CharField(required=False)
    cc_exp_yr = forms.ChoiceField(choices=get_exp_year_choices(since_founding=True, allow_null=False))
    cc_exp_mo = forms.ChoiceField(choices=get_exp_month_choices(allow_null=False))
    cc_cvv = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # self.fields['cc_number'].widget.attrs['class'] = 'cc-field'

        # Set initial values on CC fields from linked Card models
        if self.instance.card:
            self.fields['cc_number'].initial = self.instance.card.number
            self.fields['cc_exp_yr'].initial = self.instance.card.exp_year
            self.fields['cc_exp_mo'].initial = self.instance.card.exp_month
            self.fields['cc_cvv'].initial = self.instance.card.cvv

    class Meta:
        model = AdHocPayment
        # fields = '__all__'
        exclude = ('submitted_at', 'paid_at', 'card', 'confirmation_code',)


class AdHocPaymentCreateForm(CSSClassMixin, forms.ModelForm):
    phone_fields = ('phone',)

    class Meta:
        model = AdHocPayment
        fields = ('full_name', 'email', 'phone', 'amount', 'item', 'message',)


class TollTagForm(forms.ModelForm):

    tag_number = forms.CharField(required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['vehicle'].choices = get_vehicle_choices(allow_null=True)

    class Meta:
        model = TollTag
        fields = '__all__'


class TaxRateForm(CSSClassMixin, forms.ModelForm):
    short_fields = ('postal_code', 'total_rate_as_percent',)

    postal_code = USZipCodeField(required=True)
    total_rate_as_percent = forms.DecimalField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['total_rate_as_percent'].initial = self.instance.total_rate_as_percent
        # for field in ['postal_code', 'total_rate_as_percent']:
        #     self.add_widget_css_class(field, 'short')

    class Meta:
        model = TaxRate
        # fields = '__all__'
        exclude = ('country', 'total_rate',)


# class GuidedDriveForm(forms.ModelForm):
#     class Meta:
#         model = GuidedDrive
#         fields = '__all__'


class GuidedDriveForm(CSSClassMixin, CustomerSearchMixin, forms.ModelForm):
    short_fields = (
        'requested_date_picker', 'backup_date_picker', 'num_drivers', 'num_passengers', 'num_minors', 'coupon_code',
    )

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
            self.fields['requested_date_picker'].initial = self.instance.requested_date.strftime(settings.DATE_FORMAT_INPUT)
        if self.instance.backup_date:
            self.fields['backup_date_picker'].initial = self.instance.backup_date.strftime(settings.DATE_FORMAT_INPUT)
        self.fields['override_subtotal'].widget.attrs['placeholder'] = 'Override'

        # short_fields = [
        #     'requested_date_picker', 'backup_date_picker', 'num_drivers', 'num_passengers', 'num_minors', 'coupon_code'
        # ]
        # for field in short_fields:
        #     try:
        #         self.add_widget_css_class(field, 'short')
        #     except KeyError:
        #         pass

        # self.style_customer_search_fields()

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
    short_fields = ('amount', 'paid_on_picker',)

    paid_on_picker = forms.DateField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.paid_at:
            self.fields['paid_on_picker'].initial = self.instance.paid_at.strftime(settings.DATE_FORMAT_INPUT)

        # short_fields = [
        #     'amount', 'paid_on_picker'
        # ]
        # for field in short_fields:
        #     self.add_widget_css_class(field, 'short')

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


class GiftCertificateForm(CSSClassMixin, forms.ModelForm):
    cc_fields = ('cc_number',)
    phone_fields = ('cc_phone',)

    is_paid = forms.ChoiceField(choices=TRUE_FALSE_CHOICES, initial=False, required=False)
    is_used = forms.ChoiceField(choices=TRUE_FALSE_CHOICES, initial=False, required=False)

    cc_name = forms.CharField(required=False)
    cc_number = forms.CharField(required=False)
    cc_exp_yr = forms.ChoiceField(choices=get_exp_year_choices(since_founding=True, allow_null=False))
    cc_exp_mo = forms.ChoiceField(choices=get_exp_month_choices(allow_null=False))
    cc_cvv = forms.CharField(required=False)
    cc_phone = PhoneNumberField(region='US', required=False)

    value_message = forms.CharField(widget=forms.Textarea(), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['amount'].initial = 100.00

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


class StripeChargeForm(CSSClassMixin, forms.ModelForm):
    cc_fields = ('cc_number',)
    phone_fields = ('phone',)
    short_fields = (
        'zip', 'home_phone', 'mobile_phone', 'work_phone', 'fax', 'insurance_company_phone', 'discount_pct',
        'cc_cvv', 'cc2_cvv', 'phone',
        # For "Charge" view (StripeChargeChargeView) only
        'amount', 'cc_zip',
    )

    CAPTURE_CHOICES = (
        (True, 'Charge'),
        (False, 'Auth only'),
    )

    amount = forms.DecimalField(required=True)
    capture = forms.ChoiceField(choices=CAPTURE_CHOICES, initial=False)
    cc_address = forms.CharField(widget=forms.Textarea(), required=False)
    cc_exp_yr = forms.ChoiceField(choices=get_exp_year_choices(since_founding=True, allow_null=False))
    cc_exp_mo = forms.ChoiceField(choices=get_exp_month_choices(allow_null=False))
    stripe_token = forms.CharField(widget=forms.HiddenInput(), required=False)
    stripe_error = forms.CharField(widget=forms.HiddenInput(), required=False)
    stripe_error_param = forms.CharField(widget=forms.HiddenInput(), required=False)
    customer = forms.ModelChoiceField(queryset=Customer.objects.all(), widget=forms.HiddenInput(), required=False)
    card_obj = forms.ModelChoiceField(queryset=Card.objects.all(), widget=forms.HiddenInput(), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # self.fields['phone'].widget.attrs['class'] = 'phone'
        # self.fields['cc_number'].widget.attrs['class'] = 'cc-field'
        # short_fields = [
        #     'zip', 'home_phone', 'mobile_phone', 'work_phone', 'fax', 'insurance_company_phone', 'discount_pct',
        #     'cc_cvv', 'cc_phone', 'cc2_cvv', 'cc2_phone',
        # ]
        # for field in short_fields:
        #     self.add_widget_css_class(field, 'short')

        # Set initial values on CC fields from linked Card models
        if self.instance.card:
            self.fields['cc_number'].initial = self.instance.card.number
            self.fields['cc_exp_yr'].initial = self.instance.card.exp_year
            self.fields['cc_exp_mo'].initial = self.instance.card.exp_month
            self.fields['cc_cvv'].initial = self.instance.card.cvv

        if self.initial.get('customer'):
            customer = self.initial['customer']
            if isinstance(customer, Customer):
                self.fields['full_name'].initial = customer.full_name
                self.fields['email'].initial = customer.email
                self.fields['phone'].initial = customer.phone
                self.fields['cc_address'].initial = customer.address_line_1
                self.fields['cc_city'].initial = customer.city
                self.fields['cc_state'].initial = customer.state
                self.fields['cc_zip'].initial = customer.zip
                card = None
                if self.initial.get('card') == '1' and customer.card_1:
                    card = customer.card_1
                elif self.initial.get('card') == '2' and customer.card_2:
                    card = customer.card_2
                if card:
                    self.fields['cc_number'].initial = card.number
                    self.fields['cc_exp_mo'].initial = card.exp_month
                    self.fields['cc_exp_yr'].initial = card.exp_year
                    self.fields['cc_cvv'].initial = card.cvv
                    self.fields['card_obj'].initial = card.id

    def clean_amount(self):
        if self.cleaned_data['amount'] <= 0.5:
            raise forms.ValidationError('Amount must be greater than $0.50')
        return self.cleaned_data['amount']

    def clean(self):
        if self.cleaned_data['stripe_error']:
            raise forms.ValidationError(self.cleaned_data['stripe_error'])

    class Meta:
        model = Charge
        # fields = '__all__'
        exclude = ('uuid', 'card', 'stripe_customer',)


class CardForm(forms.ModelForm):

    class Meta:
        model = Card
        fields = '__all__'
        # exclude = ('uuid',)


class RedFlagForm(CSSClassMixin, forms.ModelForm):
    phone_fields = ('home_phone', 'mobile_phone',)
    short_fields = ('home_phone', 'mobile_phone', 'zip', 'ssn',)
    ssn_fields = ('ssn',)

    class Meta:
        model = RedFlag
        fields = '__all__'
        # exclude = ('confirmation_code',)


class IPBanForm(CSSClassMixin, forms.ModelForm):
    short_fields = ('ip_address', 'prefix_bits', 'expires_on',)

    expires_on = forms.DateField(widget=forms.DateInput(), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.expires_at:
            expires_at_localized = self.instance.expires_at.astimezone(pytz.timezone(settings.TIME_ZONE))
            self.fields['expires_on'].initial = expires_at_localized.strftime(settings.DATE_FORMAT_INPUT)

    def clean(self):
        super().clean()
        self.cleaned_data['expires_at'] = self.cleaned_data['expires_on']

    class Meta:
        model = IPBan
        fields = '__all__'


class DamageForm(CSSClassMixin, forms.ModelForm):
    short_fields = ('damaged_on', 'repaired_on', 'cost', 'customer_billed_amount', 'customer_paid_amount',)

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
            self.fields['damaged_on'].initial = damaged_at_localized.strftime(settings.DATE_FORMAT_INPUT)
        if self.instance.repaired_at:
            repaired_at_localized = self.instance.repaired_at.astimezone(pytz.timezone(settings.TIME_ZONE))
            self.fields['repaired_on'].initial = repaired_at_localized.strftime(settings.DATE_FORMAT_INPUT)

        # short_fields = [
        #     'damaged_on', 'repaired_on', 'cost', 'customer_billed_amount', 'customer_paid_amount',
        # ]
        # for field in short_fields:
        #     self.add_widget_css_class(field, 'short')

    def clean(self):
        super().clean()
        self.cleaned_data['damaged_at'] = self.cleaned_data['damaged_on']
        self.cleaned_data['repaired_at'] = self.cleaned_data['repaired_on']

    class Meta:
        model = Damage
        fields = '__all__'
        # exclude = ('confirmation_code',)


class ScheduledServiceForm(CSSClassMixin, forms.ModelForm):
    short_fields = ('done_on', 'done_mileage', 'next_on', 'next_mileage',)

    done_on = forms.DateField(widget=forms.DateInput(), required=False)
    next_on = forms.DateField(widget=forms.DateInput(), required=False)
    is_due = forms.ChoiceField(choices=TRUE_FALSE_CHOICES, initial=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['vehicle'].choices = get_vehicle_choices()
        if self.instance.done_at:
            done_at_localized = self.instance.done_at.astimezone(pytz.timezone(settings.TIME_ZONE))
            self.fields['done_on'].initial = done_at_localized.strftime(settings.DATE_FORMAT_INPUT)
        if self.instance.next_at:
            next_at_localized = self.instance.next_at.astimezone(pytz.timezone(settings.TIME_ZONE))
            self.fields['next_on'].initial = next_at_localized.strftime(settings.DATE_FORMAT_INPUT)

        # short_fields = [
        #     'done_on', 'done_mileage', 'next_on', 'next_mileage',
        # ]
        # for field in short_fields:
        #     self.add_widget_css_class(field, 'short')

    def clean(self):
        super().clean()
        self.cleaned_data['done_at'] = self.cleaned_data['done_on']
        self.cleaned_data['next_at'] = self.cleaned_data['next_on']

    class Meta:
        model = ScheduledService
        fields = '__all__'
        # exclude = ('confirmation_code',)


class IncidentalServiceForm(CSSClassMixin, forms.ModelForm):
    short_fields = ('done_on', 'mileage',)

    done_on = forms.DateField(widget=forms.DateInput(), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['vehicle'].choices = get_vehicle_choices()
        if self.instance.done_at:
            done_at_localized = self.instance.done_at.astimezone(pytz.timezone(settings.TIME_ZONE))
            self.fields['done_on'].initial = done_at_localized.strftime(settings.DATE_FORMAT_INPUT)

        # short_fields = [
        #     'done_on', 'mileage',
        # ]
        # for field in short_fields:
        #     self.add_widget_css_class(field, 'short')

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
