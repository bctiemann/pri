import logging
import datetime
import pytz
import math
import requests
from localflavor.us.forms import USZipCodeField, USStateField, USStateSelect

from phonenumber_field.formfields import PhoneNumberField
from creditcards.models import CardNumberField, CardExpiryField, SecurityCodeField

from django.conf import settings
from django import forms
from django.utils import timezone
from django.utils.translation import gettext_lazy as _, ngettext_lazy
from django.contrib.auth import password_validation

from fleet.models import Vehicle, VehicleMarketing, VehicleStatus
from sales.models import Reservation, Coupon, PerformanceExperience, JoyRide, GiftCertificate, AdHocPayment
from users.models import Customer
from sales.calculators import RentalPriceCalculator, PerformanceExperiencePriceCalculator, JoyRidePriceCalculator
from sales.enums import get_service_hours, TRUE_FALSE_CHOICES, get_exp_year_choices, get_exp_month_choices, get_numeric_choices
from sales.constants import BANK_PHONE_HELP_TEXT
from backoffice.forms import CSSClassMixin

logger = logging.getLogger(__name__)

current_year = timezone.now().year


# This mixin adds credit card form fields to any other form. Reservation 2nd-phase, gift cert, ad-hoc paymnt, etc.
class CardFormMixin(forms.Form):
    cc_number = forms.CharField(required=settings.COLLECT_CARD_INFO)
    cc_exp_yr = forms.ChoiceField(choices=get_exp_year_choices(), required=settings.COLLECT_CARD_INFO)
    cc_exp_mo = forms.ChoiceField(choices=get_exp_month_choices(), required=settings.COLLECT_CARD_INFO)
    cc_cvv = forms.CharField(required=settings.COLLECT_CARD_INFO)
    cc_phone = PhoneNumberField(help_text=BANK_PHONE_HELP_TEXT, required=settings.COLLECT_CARD_INFO)


# This mixin can be added to any form to enforce checking a g-recaptcha-response field included in the form.data.
class ReCAPTCHAFormMixin(forms.Form):
    recaptcha = forms.CharField(required=False)

    @staticmethod
    def verify_recaptcha(recaptcha_response):
        payload = {
            'secret': settings.RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response,
        }
        return requests.post(settings.RECAPTCHA_VERIFY_URL, data=payload)

    def clean(self):
        response = super().clean()
        # TODO: Option to redirect failing captcha submissions to honeypot success page
        if settings.RECAPTCHA_ENABLED:
            recaptcha_response = self.data.get('g-recaptcha-response')
            if recaptcha_response:
                recaptcha_verify_response = self.verify_recaptcha(recaptcha_response)
                recaptcha_result = recaptcha_verify_response.json()
            else:
                recaptcha_result = {'success': False}
            if not recaptcha_result['success']:
                self.add_error('recaptcha', forms.ValidationError(_("CAPTCHA failure.")))
        return response


# Reusable mixin for collecting all customer and payment data for the 2nd-phase form, used in reservations, joy rides,
# performance experiences
class PaymentFormMixin(CSSClassMixin, forms.Form):

    error_messages = {
        'password_mismatch': _('The two password fields didn’t match.'),
    }

    cc_fields = ('cc_number',)
    phone_fields = ('mobile_phone', 'work_phone', 'home_phone', 'fax', 'cc_phone',)

    first_name = forms.CharField()
    last_name = forms.CharField()
    mobile_phone = PhoneNumberField(required=False)
    work_phone = PhoneNumberField(required=False)
    home_phone = PhoneNumberField(required=False)
    fax = PhoneNumberField(required=False)
    address_line_1 = forms.CharField()
    address_line_2 = forms.CharField(required=False)
    city = forms.CharField()
    state = USStateField(widget=USStateSelect())
    zip = USZipCodeField()

    password_new = forms.CharField(widget=forms.PasswordInput())
    password_repeat = forms.CharField(widget=forms.PasswordInput())

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     for field in self.cc_fields:
    #         self.add_widget_css_class(field, 'cc-field')
    #     for field in self.phone_fields:
    #         self.add_widget_css_class(field, 'phone')

    def clean_password_repeat(self):
        password1 = self.cleaned_data.get('password_new')
        password2 = self.cleaned_data.get('password_repeat')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )
        password_validation.validate_password(password2, user=None)
        return password2


# This dumbed-down error handler finds the "main" error out of a form, and returns a single string.
class FormErrorMixin:
    def get_error(self):
        if self.is_valid():
            return None
        if self.non_field_errors():
            return self.non_field_errors()[0]
        return f'{list(self.errors.keys())[0]}: {list(self.errors.values())[0][0]}'


# Rental forms

# 1st phase: Rental Details

class ReservationRentalDetailsForm(FormErrorMixin, forms.ModelForm):
    error_css_class = 'field-error'
    DRIVERS_CHOICES = (
        (1, '1'),
        (2, '2'),
        (3, _('More than 2')),
    )
    DELIVERY_REQUIRED_CHOICES = (
        (0, _(f'I will be picking up the vehicle at PRI in {settings.COMPANY_CITY_FOR_DELIVERY}')),
        (1, _('I would like the vehicle to be delivered to me')),
    )
    DATETIME_FORMAT = '%m/%d/%Y %H:%M'
    discount = None
    customer = None
    vehicle = None
    form_type = 'details'

    # It is not necessary to explicitly define form fields on this class if they are defined in the model class,
    # except to override certain default behaviors such as choice values or widget attributes. We must define
    # additional fields here if they do not exist in the model referenced in Meta (i.e. Reservation).

    vehicle_marketing = forms.ModelChoiceField(
        widget=forms.HiddenInput(),
        queryset=VehicleMarketing.objects.filter(status=VehicleStatus.READY)
    )
    out_date = forms.DateField(widget=forms.DateInput(
        attrs={'placeholder': 'MM/DD/YYYY', 'class': 'short'}),
        error_messages={'required': 'Please specify the date of the rental.'},
    )
    out_time = forms.TimeField(widget=forms.Select(choices=get_service_hours()))
    out_at = forms.DateTimeField(required=False)
    back_date = forms.DateField(widget=forms.DateInput(
        attrs={'placeholder': 'MM/DD/YYYY', 'class': 'short'}),
        error_messages={'required': 'Please specify the date when you\'ll be returning the vehicle.'},
    )
    back_time = forms.TimeField(widget=forms.Select(choices=get_service_hours()))
    back_at = forms.DateTimeField(required=False)
    drivers = forms.ChoiceField(choices=DRIVERS_CHOICES)
    delivery_required = forms.ChoiceField(choices=DELIVERY_REQUIRED_CHOICES)
    delivery_zip = USZipCodeField(required=False)
    extra_miles = forms.ChoiceField()
    email = forms.EmailField()
    coupon_code = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': '(Optional)'}))
    # TypedChoiceField is necessary when the form is being serialized via FE/JS and values are sent as 'True'/'False'
    # is_military = forms.ChoiceField(choices=TRUE_FALSE_CHOICES, initial=False)
    is_military = forms.TypedChoiceField(coerce=lambda x: x == 'True', initial=False, choices=TRUE_FALSE_CHOICES, required=False)
    notes = forms.CharField(widget=forms.Textarea(), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['extra_miles'].choices = ((k, v['label']) for k, v in settings.EXTRA_MILES_PRICES.items())
        self.fields['delivery_zip'].widget.attrs['class'] = 'short'

    def is_valid(self):
        return super().is_valid()

    def clean_out_at(self):
        if "out_date" not in self.data:
            raise forms.ValidationError(_('Invalid rental date.'))
        try:
            date_str = f'{self.data["out_date"]} {self.data["out_time"]}'
            out_at = datetime.datetime.strptime(date_str, self.DATETIME_FORMAT)
        except ValueError:
            raise forms.ValidationError(_('Invalid rental date.'))

        out_at = pytz.timezone(settings.TIME_ZONE).localize(out_at)

        if out_at < timezone.now():
            raise forms.ValidationError(_("You've specified a rental date in the past."))

        return out_at

    def clean_back_at(self):
        out_at = self.clean_out_at()
        try:
            date_str = f'{self.data["back_date"]} {self.data["back_time"]}'
            back_at = datetime.datetime.strptime(date_str, self.DATETIME_FORMAT)
        except ValueError:
            raise forms.ValidationError(_('Invalid return date.'))

        back_at = pytz.timezone(settings.TIME_ZONE).localize(back_at)

        if back_at < out_at:
            raise forms.ValidationError(_("You've specified a return date earlier than the rental date."))

        rental_duration = back_at - out_at

        if rental_duration.total_seconds() < 20 * 3600:
            rental_duration_hours = rental_duration.total_seconds() / 3600
            if rental_duration_hours == int(rental_duration_hours):
                rental_duration_hours = int(rental_duration_hours)
            rental_duration_hours_plural = 's' if rental_duration_hours != 1 else ''
            raise forms.ValidationError(_(
                f"You've specified a rental of only {rental_duration_hours} hour{rental_duration_hours_plural}. "
                f"Please note that we do not rent for less than 24 hours at a time."
            ))

        return back_at

    # Call clean_out_at() and clean_back_at() to ingest their validation errors into these fields, which are the ones
    # reflected in the actual form HTML and need to receive the error CSS class
    def clean_out_date(self):
        self.clean_out_at()
        return self.cleaned_data['out_date']

    def clean_back_date(self):
        self.clean_back_at()
        return self.cleaned_data['back_date']

    def clean_delivery_required(self):
        return bool(int(self.cleaned_data.get('delivery_required', False)))

    def clean_delivery_zip(self):
        delivery_required = self.clean_delivery_required()
        if delivery_required and not self.cleaned_data['delivery_zip']:
            raise forms.ValidationError('Please specify the ZIP code for delivery.')
        return self.cleaned_data['delivery_zip']

    def clean(self):
        # TODO: Handle KeyError better
        try:
            self.customer = Customer.objects.get(user__email=self.cleaned_data['email'])
        except (Customer.DoesNotExist, KeyError):
            pass

        if not 'vehicle_marketing' in self.cleaned_data:
            raise forms.ValidationError('Invalid vehicle specified.')

        self.vehicle = Vehicle.objects.filter(vehicle_marketing_id=self.cleaned_data['vehicle_marketing'].id).first()

        vehicle_marketing = self.vehicle.vehicle_marketing
        self.cleaned_data['miles_included'] = vehicle_marketing.miles_included
        self.cleaned_data['deposit_amount'] = vehicle_marketing.security_deposit

        return super().clean()

    @property
    def tax_zip(self):
        return self.cleaned_data.get('delivery_zip') or settings.DEFAULT_TAX_ZIP

    @property
    def price_data(self):
        if not self.is_bound:
            return None
        if not self.vehicle:
            return {}
        price_calculator = RentalPriceCalculator(
            vehicle_marketing=self.cleaned_data.get('vehicle_marketing'),
            num_days=self.instance.num_days,
            extra_miles=self.cleaned_data.get('extra_miles') or 0,
            coupon_code=self.cleaned_data.get('coupon_code'),
            email=self.cleaned_data.get('email'),
            tax_zip=self.tax_zip,
            effective_date=self.cleaned_data.get('out_date'),
            is_military=self.cleaned_data.get('is_military'),
        )
        return price_calculator.get_price_data()

    class Meta:
        model = Reservation
        # fields = '__all__'
        exclude = ('confirmation_code', 'status',)


# 2nd-phase form; extends ReservationRentalDetailsForm (with PaymentFormMixin which includes all the Customer fields)
# so it inherits all the first form's validations
class ReservationRentalPaymentForm(PaymentFormMixin, CardFormMixin, ReservationRentalDetailsForm):
    form_type = 'payment'


# If the customer already exists, this form will be shown and processed instead of ReservationRentalPaymentForm
class ReservationRentalLoginForm(ReservationRentalDetailsForm):
    form_type = 'login'

    password = forms.CharField(widget=forms.PasswordInput(), required=False)


# GuidedDrive 1st-phase form; used for both Joy Ride and Performance Experience (both are subclassed below)

class GuidedDriveBaseDetailsForm(forms.Form):

    error_css_class = 'field-error'
    discount = None
    customer = None

    num_passengers = forms.TypedChoiceField(coerce=lambda x: int(x), choices=get_numeric_choices(min_val=1, max_val=4))
    # num_minors = forms.TypedChoiceField(coerce=lambda x: int(x), choices=get_numeric_choices(min_val=0, max_val=4))
    requested_date = forms.DateField(widget=forms.DateInput(
        attrs={'placeholder': 'MM/DD/YYYY', 'class': 'short'}),
        error_messages={'required': 'Please specify your preferred date for the event.'},
    )
    backup_date = forms.DateField(widget=forms.DateInput(
        attrs={'placeholder': 'MM/DD/YYYY', 'class': 'short'}),
        error_messages={'required': 'Please provide an alternate date for the event.'},
        help_text='We\'ll do our best to accommodate your first choice of date, but please pick an alternate just in case.'
    )
    email = forms.EmailField()
    big_and_tall = forms.TypedChoiceField(
        coerce=lambda x: x == 'True', initial=False,
        choices=TRUE_FALSE_CHOICES,
        help_text='If anyone in your party is especially big or tall, please let us know so we can make sure everyone is comfortable.',
    )
    coupon_code = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': '(Optional)'}))

    def clean_requested_date(self):
        if self.cleaned_data['requested_date'] < timezone.now().date():
            raise forms.ValidationError(_("You've specified a date in the past."))
        return self.cleaned_data['requested_date']

    def clean_backup_date(self):
        if self.cleaned_data['backup_date'] < timezone.now().date():
            raise forms.ValidationError(_("You've specified a date in the past."))
        return self.cleaned_data['backup_date']

    def clean(self):
        logger.debug('cleaned:')
        logger.debug(self.cleaned_data)
        # TODO: Handle KeyError better
        try:
            self.customer = Customer.objects.get(user__email=self.cleaned_data['email'])
        except (Customer.DoesNotExist, KeyError):
            pass

        if not any((
                self.cleaned_data['vehicle_choice_1'],
                self.cleaned_data['vehicle_choice_2'],
                self.cleaned_data['vehicle_choice_3'],
        )):
            raise forms.ValidationError(_("Please select at least one and up to three vehicles for your event."))

        if self.cleaned_data.get('backup_date') == self.cleaned_data.get('requested_date'):
            self.add_error('backup_date', forms.ValidationError(_("Alternate date can't be the same as the requested date.")))

        return super().clean()

    @property
    def tax_zip(self):
        return settings.DEFAULT_TAX_ZIP

    @property
    def price_data(self):
        raise NotImplementedError


# Joy Ride

class JoyRideDetailsForm(GuidedDriveBaseDetailsForm, forms.ModelForm):
    form_type = 'details'

    num_minors = forms.TypedChoiceField(coerce=lambda x: int(x), choices=get_numeric_choices(min_val=0, max_val=4))

    @property
    def price_data(self):
        if not self.is_bound:
            return None
        price_calculator = JoyRidePriceCalculator(
            num_passengers=self.cleaned_data.get('num_passengers'),
            coupon_code=self.cleaned_data.get('coupon_code'),
            email=self.cleaned_data.get('email'),
            tax_zip=self.tax_zip,
            effective_date=self.cleaned_data.get('out_date'),
            is_military=self.cleaned_data.get('is_military'),
        )
        return price_calculator.get_price_data()

    class Meta:
        model = JoyRide
        exclude = ('confirmation_code', 'status',)


class JoyRidePaymentForm(PaymentFormMixin, CardFormMixin, ReCAPTCHAFormMixin, JoyRideDetailsForm):
    form_type = 'payment'


class JoyRideLoginForm(JoyRideDetailsForm):
    form_type = 'login'

    password = forms.CharField(widget=forms.PasswordInput(), required=False)


# Performance Experience

class PerformanceExperienceDetailsForm(GuidedDriveBaseDetailsForm, forms.ModelForm):
    form_type = 'details'

    DRIVERS_CHOICES = (
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, 'More than 4 (will call)'),
    )

    PASSENGERS_CHOICES = (
        (0, '0'),
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, 'More than 4 (will call)'),
    )

    num_drivers = forms.TypedChoiceField(coerce=lambda x: int(x), choices=DRIVERS_CHOICES)
    num_passengers = forms.TypedChoiceField(coerce=lambda x: int(x), choices=PASSENGERS_CHOICES)

    @property
    def price_data(self):
        if not self.is_bound:
            return None
        price_calculator = PerformanceExperiencePriceCalculator(
            num_drivers=self.cleaned_data.get('num_drivers'),
            num_passengers=self.cleaned_data.get('num_passengers'),
            coupon_code=self.cleaned_data.get('coupon_code'),
            email=self.cleaned_data.get('email'),
            tax_zip=self.tax_zip,
            effective_date=self.cleaned_data.get('out_date'),
            is_military=self.cleaned_data.get('is_military'),
        )
        return price_calculator.get_price_data()

    class Meta:
        model = PerformanceExperience
        exclude = ('confirmation_code', 'status',)


class PerformanceExperiencePaymentForm(PaymentFormMixin, CardFormMixin, PerformanceExperienceDetailsForm):
    form_type = 'payment'


class PerformanceExperienceLoginForm(PerformanceExperienceDetailsForm):
    form_type = 'login'

    password = forms.CharField(widget=forms.PasswordInput(), required=False)


class GiftCertificateForm(CSSClassMixin, CardFormMixin, forms.ModelForm):

    AMOUNT_CHOICES = (
        (100, '$100'),
        (250, '$250'),
        (500, '$500'),
        (1000, '$1,000'),
        (1500, '$1,500'),
        (2000, '$2,000'),
        (5000, '$5,000'),
    )

    cc_fields = ('cc_number',)
    phone_fields = ('phone', 'cc_phone',)

    amount = forms.TypedChoiceField(coerce=lambda x: int(x), choices=AMOUNT_CHOICES)
    message = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': '(Optional)'}))

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     for field in self.cc_fields:
    #         self.add_widget_css_class(field, 'cc-field')
    #     for field in self.phone_fields:
    #         self.add_widget_css_class(field, 'phone')

    class Meta:
        model = GiftCertificate
        fields = '__all__'


class AdHocPaymentForm(CardFormMixin, CSSClassMixin, forms.ModelForm):
    cc_fields = ('cc_number',)
    phone_fields = ('phone',)

    cc_phone = PhoneNumberField(required=False)

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     for field in self.cc_fields:
    #         self.add_widget_css_class(field, 'cc-field')
    #     for field in self.phone_fields:
    #         self.add_widget_css_class(field, 'phone')

    class Meta:
        model = AdHocPayment
        exclude = ('confirmation_code', 'is_paid', 'is_submitted', 'item', 'amount', 'message',)
