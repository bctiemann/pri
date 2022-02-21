from phonenumber_field.formfields import PhoneNumberField

from django import forms
from django.utils.translation import gettext_lazy as _

from sales.enums import get_exp_year_choices, get_exp_month_choices
from sales.models import BaseReservation
from users.models import Customer


class PasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput())
    password_repeat = forms.CharField(widget=forms.PasswordInput())


class ReservationCustomerInfoForm(forms.ModelForm):

    confirmation_code = forms.CharField(widget=forms.HiddenInput())

    insurance_company = forms.CharField(required=True, error_messages={'required': _("Please enter the driver's insurance carrier.")})
    insurance_policy_number = forms.CharField(required=True, error_messages={'required': _("Please enter the driver's insurance policy number.")})

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
    cc2_instructions = forms.CharField(widget=forms.Textarea(), required=False)

    def __init__(self, *args, confirmation_code=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['confirmation_code'].initial = confirmation_code

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
            'first_name', 'last_name', 'date_of_birth', 'address_line_1', 'address_line_2', 'city', 'state', 'zip',
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

    customer_notes = forms.CharField(widget=forms.Textarea())

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     print('foo')
        # self.fields['confirmation_code'].initial = confirmation_code

    class Meta:
        model = BaseReservation
        fields = ('customer_notes',)


class AccountDriverInfoForm(forms.ModelForm):

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
