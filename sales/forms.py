import datetime
import pytz
import math
from localflavor.us.forms import USZipCodeField
from phonenumber_field.formfields import PhoneNumberField
from creditcards.models import CardNumberField, CardExpiryField, SecurityCodeField

from django.conf import settings
from django import forms
from django.utils import timezone
from django.utils.translation import gettext_lazy as _, ngettext_lazy

from fleet.models import Vehicle, VehicleMarketing, VehicleStatus
from sales.models import Reservation, Coupon
from users.models import Customer
from sales.utils import RentalPriceCalculator

current_year = timezone.now().year


# Rental forms

# 1st phase: Rental Details

class ReservationRentalDetailsForm(forms.ModelForm):
    error_css_class = 'field-error'
    TIME_CHOICES = (
        ('07:00', '7:00 am'),
        ('07:30', '7:30 am'),
        ('08:00', '8:00 am'),
        ('08:30', '8:30 am'),
        ('09:00', '9:00 am'),
        ('09:30', '9:30 am'),
        ('10:00', '10:00 am'),
        ('10:30', '10:30 am'),
        ('11:00', '11:00 am'),
        ('11:30', '11:30 am'),
        ('12:00', '12:00 pm'),
        ('12:30', '12:30 pm'),
        ('13:00', '1:00 pm'),
        ('13:30', '1:30 pm'),
        ('14:00', '2:00 pm'),
        ('14:30', '2:30 pm'),
        ('15:00', '3:00 pm'),
        ('15:30', '3:30 pm'),
        ('16:00', '4:00 pm'),
        ('16:30', '4:30 pm'),
        ('17:00', '5:00 pm'),
        ('17:30', '5:30 pm'),
        ('18:00', '6:00 pm'),
        ('18:30', '6:30 pm'),
        ('19:00', '7:00 pm'),
        ('19:30', '7:30 pm'),
        ('20:00', '8:00 pm'),
        ('23:00', 'Other (special)'),
    )
    DRIVERS_CHOICES = (
        (1, '1'),
        (2, '2'),
        (3, _('More than 2')),
    )
    DELIVERY_CHOICES = (
        (0, _('I will be picking up the vehicle at PRI in Ringwood, NJ')),
        (1, _('I would like the vehicle to be delivered to me')),
    )
    TRUE_FALSE_CHOICES = (
        (True, 'Yes'),
        (False, 'No')
    )
    DATETIME_FORMAT = '%m/%d/%Y %H:%M'
    discount = None
    customer = None
    vehicle = None

    # It is not necessary to explicitly define form fields on this class if they are defined in the model class,
    # except to override certain default behaviors such as choice values or widget attributes. We must define
    # additional fields here if they do not exist in the model referenced in Meta (Reservation).

    vehicle_marketing = forms.ModelChoiceField(widget=forms.HiddenInput(), queryset=VehicleMarketing.objects.filter(status=VehicleStatus.READY))
    out_date = forms.DateField(widget=forms.DateInput(attrs={'placeholder': 'MM/DD/YYYY'}))
    out_time = forms.TimeField(widget=forms.Select(choices=TIME_CHOICES))
    out_at = forms.DateTimeField(required=False)
    back_date = forms.DateField(widget=forms.DateInput(attrs={'placeholder': 'MM/DD/YYYY'}))
    back_time = forms.TimeField(widget=forms.Select(choices=TIME_CHOICES))
    back_at = forms.DateTimeField(required=False)
    drivers = forms.ChoiceField(choices=DRIVERS_CHOICES)
    delivery_required = forms.ChoiceField(choices=DELIVERY_CHOICES)
    delivery_zip = USZipCodeField(required=False)
    extra_miles = forms.ChoiceField()
    email = forms.EmailField()
    coupon_code = forms.CharField(required=False)
    is_military = forms.TypedChoiceField(coerce=lambda x: x == 'True', initial=False, choices=TRUE_FALSE_CHOICES)
    notes = forms.CharField(widget=forms.Textarea(), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['extra_miles'].choices = ((k, v['label']) for k, v in settings.EXTRA_MILES_PRICES.items())

    def is_valid(self):
        return super().is_valid()

    def clean_out_at(self):
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
        return bool(int(self.cleaned_data['delivery_required']))

    def clean_delivery_zip(self):
        delivery_required = self.clean_delivery_required()
        if delivery_required and not self.cleaned_data['delivery_zip']:
            raise forms.ValidationError('Please specify the ZIP code for delivery.')
        return self.cleaned_data['delivery_zip']

    def clean(self):
        print('cleaned:')
        print(self.cleaned_data)
        try:
            self.customer = Customer.objects.get(user__email=self.cleaned_data['email'])
        except (Customer.DoesNotExist, KeyError):
            pass
        try:
            self.vehicle = Vehicle.objects.get(pk=self.cleaned_data['vehicle_marketing'].vehicle_id)
        except Vehicle.DoesNotExist:
            raise forms.ValidationError(f"Vehicle {self.cleaned_data['vehicle_marketing']} mapped incorrectly.")
        return super().clean()

    @property
    def rental_duration(self):
        try:
            return self.cleaned_data['back_at'] - self.cleaned_data['out_at']
        except (KeyError, TypeError):
            return datetime.timedelta(seconds=0)

    @property
    def num_days(self):
        return math.ceil(self.rental_duration.total_seconds() / 86400)

    @property
    def tax_zip(self):
        return self.cleaned_data.get('delivery_zip') or settings.DEFAULT_TAX_ZIP

    # @property
    # def raw_cost(self):
    #     return self.cleaned_data['vehicle_marketing'].price_per_day * self.num_days
    #
    # def coupon_discount(self, value):
    #     if not self.discount:
    #         coupon_code = self.cleaned_data['coupon_code']
    #         if not coupon_code:
    #             return 0
    #         try:
    #             self.discount = Coupon.objects.get(code=coupon_code)
    #         except Discount.DoesNotExist:
    #             return 0
    #     return self.discount.get_discount_value(value)
    #
    # def customer_discount(self, value):
    #     print(self.customer)
    #     if self.customer:
    #         return value * self.customer.discount_pct / 100
    #     return 0
    #
    # @property
    # def sales_tax(self):
    #     return 0
    #
    # @property
    # def subtotal(self):
    #     subtotal = self.raw_cost
    #     print(subtotal)
    #
    #     # Multi-day discount
    #
    #     # Coupon discount
    #     coupon_discount = self.coupon_discount(subtotal)
    #     subtotal -= coupon_discount
    #     print(subtotal)
    #
    #     # Customer discount
    #     customer_discount = self.customer_discount(subtotal)
    #     subtotal -= customer_discount
    #     print(subtotal)
    #
    #     # Extra miles
    #
    #     # Sales tax
    #
    #     return subtotal
    #
    # @property
    # def total_with_tax(self):
    #     return 0

    @property
    def price_data(self):
        price_calculator = RentalPriceCalculator(
            vehicle_marketing=self.cleaned_data['vehicle_marketing'],
            num_days=self.num_days,
            extra_miles=self.cleaned_data['extra_miles'],
            coupon_code=self.cleaned_data.get('coupon_code'),
            email=self.cleaned_data.get('email'),
            tax_zip=self.tax_zip,
            effective_date=self.cleaned_data.get('out_date'),
            is_military=self.cleaned_data.get('is_military'),
        )
        return price_calculator.get_price_data()
        # subtotal = self.subtotal
        # return dict(
        #     rental_duration=self.rental_duration,
        #     num_days=self.num_days,
        #     sales_tax=self.sales_tax,
        #     customer_id=None,
        #     num_drivers=None,
        #     total_cost_raw=self.raw_cost,
        #     total_cost=None,
        #     coupon_discount=self.coupon_discount(self.raw_cost),
        #     customer_discount=self.customer_discount(self.raw_cost),
        #     customer_discount_pct=None,
        #     multi_day_discount=0,
        #     multi_day_discount_pct=None,
        #     extra_miles=None,
        #     extra_miles_cost=0,
        #     subtotal=self.subtotal,
        #     total_with_tax=self.total_with_tax,
        #     reservation_deposit=0,
        #     tax_amount=0,
        #     delivery=None,
        #     deposit=0,
        # )
        """
        <cfset numdays = (rental_duration - 1) / 24>

        <cfset result['rental_duration'] = rental_duration>
        <cfset result['salesTax'] = salesTax>
        <cfset result['tax_rate'] = totalTax>
        <cfset result['customerid'] = Customer.customerid>

        <cfset result['numdays'] = Ceiling(numdays)>
        <cfset result['numdrivers'] = IsDefined("drivers") ? drivers : "">
        <cfset result['tcostRaw'] = tcostRaw>
        <cfset result['tcost'] = tcost>
        <cfset result['car_discount'] = ds1>
        <cfset result['customer_discount'] = ds2>
        <cfset result['customer_discount_pct'] = d2>
        <cfset result['multi_day_discount_pct'] = dMultiDay>
        <cfset result['multi_day_discount'] = dMultiDay ? (Round(tcostRaw * 100) - Round(tcost * 100)) / 100 : 0>
        <cfset result['extra_miles'] = extramiles>
        <cfset result['extra_miles_cost'] = xmi>
        <cfset result['subtotal'] = s2>
        <cfset result['total_w_tax'] = taxtot>
        <cfset result['reservation_deposit'] = taxtot/2>
        <cfset result['tax_amt'] = taxmt>
        <cfset result['delivery'] = delivery>
        <cfset result['deposit'] = VFront.deposit>
        """

    class Meta:
        model = Reservation
        # fields = '__all__'
        exclude = ('confirmation_code', 'status',)


# 2nd-phase form; extends ReservationRentalDetailsForm with Customer fields so it inherits all the first form's validations
class ReservationRentalPaymentForm(ReservationRentalDetailsForm):
    customer_fields = (
        'first_name', 'last_name', 'mobile_phone', 'home_phone', 'work_phone', 'fax', 'cc_number', 'cc_exp_yr',
        'cc_exp_mo', 'cc_cvv', 'cc_phone', 'address_line_1', 'address_line_2', 'city', 'state', 'zip'
    )
    EXP_MONTH_CHOICES = (
        ('01', 'January (01)'),
        ('02', 'February (02)'),
        ('03', 'March (03)'),
        ('04', 'April (04)'),
        ('05', 'May (05)'),
        ('06', 'June (06)'),
        ('07', 'July (07)'),
        ('08', 'August (08)'),
        ('09', 'September (09)'),
        ('10', 'October (10)'),
        ('11', 'November (11)'),
        ('12', 'December (12)'),
    )
    EXP_YEAR_CHOICES = ((year, year) for year in range(current_year, current_year + 11))

    # first_name = forms.CharField()
    # last_name = forms.CharField()
    # mobile_phone = PhoneNumberField()
    # home_phone = PhoneNumberField()
    # work_phone = PhoneNumberField()
    # fax = PhoneNumberField()
    cc_number = forms.CharField()
    cc_exp_yr = forms.ChoiceField(choices=EXP_YEAR_CHOICES)
    cc_exp_mo = forms.ChoiceField(choices=EXP_MONTH_CHOICES)
    cc_cvv = forms.CharField()
    cc_phone = PhoneNumberField()
    # password = forms.CharField(widget=forms.PasswordInput(), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # current_year = timezone.now().year
        # self.fields['cc_exp_yr'].choices = ((year, year) for year in range(current_year, current_year + 11))
        # self.fields['extra_miles'].choices = ((k, v['label']) for k, v in settings.EXTRA_MILES_PRICES.items())

    class Meta:
        model = Customer
        fields = '__all__'


# If the customer already exists, this form will be shown and processed instead of ReservationRentalPaymentForm
class ReservationRentalLoginForm(ReservationRentalDetailsForm):

    password = forms.CharField(widget=forms.PasswordInput(), required=False)
