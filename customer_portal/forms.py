from phonenumber_field.formfields import PhoneNumberField

from django.conf import settings
from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import password_validation

from sales.models import BaseReservation, JoyRide, PerformanceExperience
from sales.forms import ReservationRentalDetailsForm, JoyRideDetailsForm, PerformanceExperienceDetailsForm
from users.models import Customer
from backoffice.forms import CSSClassMixin
from sales.enums import get_service_hours, TRUE_FALSE_CHOICES, get_exp_year_choices, get_exp_month_choices


class PasswordForm(forms.Form):

    error_messages = {
        'password_mismatch': _('The two password fields didn’t match.'),
    }

    password = forms.CharField(widget=forms.PasswordInput())
    password_repeat = forms.CharField(widget=forms.PasswordInput())

    def clean_password_repeat(self):
        password1 = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password_repeat')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )
        password_validation.validate_password(password2, user=None)
        return password2


class CustomerCardPrimaryForm(CSSClassMixin, forms.ModelForm):

    cc_fields = ['cc_number']
    phone_fields = ['cc_phone']

    cc_number = forms.CharField()
    cc_exp_yr = forms.ChoiceField(choices=get_exp_year_choices(since_founding=False, allow_null=False))
    cc_exp_mo = forms.ChoiceField(choices=get_exp_month_choices(allow_null=False))
    cc_cvv = forms.CharField()

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #
    #     for field in self.cc_fields:
    #         self.add_widget_css_class(field, 'cc-field')
    #     for field in self.phone_fields:
    #         self.add_widget_css_class(field, 'phone')

    # TODO: clean_cc_number

    class Meta:
        model = Customer
        fields = ('cc_number', 'cc_exp_mo', 'cc_exp_yr', 'cc_cvv', 'cc_phone',)


class CustomerCardSecondaryForm(CSSClassMixin, forms.ModelForm):

    cc_fields = ['cc2_number']
    phone_fields = ['cc2_phone']

    cc2_number = forms.CharField()
    cc2_exp_yr = forms.ChoiceField(choices=get_exp_year_choices(since_founding=False, allow_null=False))
    cc2_exp_mo = forms.ChoiceField(choices=get_exp_month_choices(allow_null=False))
    cc2_cvv = forms.CharField()

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #
    #     for field in self.cc_fields:
    #         self.add_widget_css_class(field, 'cc-field')
    #     for field in self.phone_fields:
    #         self.add_widget_css_class(field, 'phone')

    # TODO: clean_cc2_number

    class Meta:
        model = Customer
        fields = ('cc2_number', 'cc2_exp_mo', 'cc2_exp_yr', 'cc2_cvv', 'cc2_phone',)


class ReservationCustomerInfoForm(CSSClassMixin, forms.ModelForm):

    cc_fields = ['cc_number', 'cc2_number']
    phone_fields = ['mobile_phone', 'home_phone', 'work_phone', 'fax', 'insurance_company_phone', 'cc_phone', 'cc2_phone']

    confirmation_code = forms.CharField(widget=forms.HiddenInput())

    insurance_company = forms.CharField(required=True, error_messages={'required': _("Please enter the driver's insurance carrier.")})
    insurance_policy_number = forms.CharField(required=True, error_messages={'required': _("Please enter the driver's insurance policy number.")})

    # Make a proxy date_of_birth field here so we can override the displayed date format from YYYY-MM-DD to MM/DD/YYYY
    date_of_birth_date = forms.DateField()

    cc_number = forms.CharField(required=False)
    cc_exp_yr = forms.ChoiceField(required=False, choices=get_exp_year_choices(since_founding=True, allow_null=False))
    cc_exp_mo = forms.ChoiceField(required=False, choices=get_exp_month_choices(allow_null=False))
    cc_cvv = forms.CharField(required=False)

    cc2_number = forms.CharField(required=False)
    cc2_exp_yr = forms.ChoiceField(required=False, choices=get_exp_year_choices(since_founding=True, allow_null=True))
    cc2_exp_mo = forms.ChoiceField(choices=get_exp_month_choices(allow_null=True), required=False)
    cc2_cvv = forms.CharField(required=False)
    cc2_instructions = forms.CharField(widget=forms.Textarea(), required=False)

    def __init__(self, *args, confirmation_code=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['confirmation_code'].initial = confirmation_code
        if self.instance.date_of_birth:
            self.fields['date_of_birth_date'].initial = self.instance.date_of_birth.strftime(settings.DATE_FORMAT_INPUT)

        # for field in self.cc_fields:
        #     self.add_widget_css_class(field, 'cc-field')
        # for field in self.phone_fields:
        #     self.add_widget_css_class(field, 'phone')

    def clean(self):
        if not any((
            self.cleaned_data.get('mobile_phone'),
            self.cleaned_data.get('work_phone'),
            self.cleaned_data.get('home_phone'),
        )):
            raise forms.ValidationError('Please enter at least one preferred phone number.')
        self.cleaned_data['date_of_birth'] = self.cleaned_data['date_of_birth_date']

    class Meta:
        model = Customer
        fields = (
            'first_name', 'last_name', 'date_of_birth', 'date_of_birth_date', 'address_line_1', 'address_line_2', 'city', 'state', 'zip',
            'mobile_phone', 'work_phone', 'home_phone', 'fax', 'license_number', 'license_state',
            'cc_number', 'cc_exp_mo', 'cc_exp_yr', 'cc_cvv', 'cc_phone',
            'cc2_number', 'cc2_exp_mo', 'cc2_exp_yr', 'cc2_cvv', 'cc2_phone', 'cc2_instructions',
            'insurance_company', 'insurance_policy_number', 'insurance_company_phone', 'music_genre', 'music_favorite',
        )
        # fields = '__all__'


class ReservationCustomerEmptyForm(forms.ModelForm):

    def __init__(self, *args, confirmation_code=None, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = Customer
        fields = ()


class ReservationNotesForm(forms.ModelForm):

    customer_notes = forms.CharField(widget=forms.Textarea(), required=False)

    class Meta:
        model = BaseReservation
        fields = ('customer_notes',)


class ReservationDetailsForm(ReservationRentalDetailsForm):
    pass


class JoyRideNotesForm(forms.ModelForm):
    customer_notes = forms.CharField(widget=forms.Textarea(), required=False)

    class Meta:
        model = JoyRide
        fields = ('customer_notes',)


class PerformanceExperienceNotesForm(forms.ModelForm):
    customer_notes = forms.CharField(widget=forms.Textarea(), required=False)

    class Meta:
        model = PerformanceExperience
        fields = ('customer_notes',)


class AccountDriverInfoForm(CSSClassMixin, forms.ModelForm):
    phone_fields = ('mobile_phone', 'work_phone', 'home_phone', 'fax',)

    def clean_license_number(self):
        return self.instance.license_number or self.cleaned_data['license_number']

    def clean_license_state(self):
        return self.instance.license_state or self.cleaned_data['license_state']

    def clean_date_of_birth(self):
        return self.instance.date_of_birth or self.cleaned_data['date_of_birth']

    def clean(self):
        if not any((
            self.cleaned_data.get('mobile_phone'),
            self.cleaned_data.get('work_phone'),
            self.cleaned_data.get('home_phone'),
        )):
            raise forms.ValidationError('Please enter at least one preferred phone number.')

    class Meta:
        model = Customer
        fields = (
            'date_of_birth', 'address_line_1', 'address_line_2', 'city', 'state', 'zip',
            'mobile_phone', 'work_phone', 'home_phone', 'fax', 'license_number', 'license_state',
        )


class AccountInsuranceForm(forms.ModelForm):
    insurance_company = forms.CharField(required=True, error_messages={'required': _("Please enter the driver's insurance carrier.")})
    insurance_policy_number = forms.CharField(required=True, error_messages={'required': _("Please enter the driver's insurance policy number.")})

    class Meta:
        model = Customer
        fields = ('insurance_company', 'insurance_policy_number', 'insurance_company_phone',)


class AccountMusicPrefsForm(forms.ModelForm):

    class Meta:
        model = Customer
        fields = ('music_genre', 'music_favorite',)
