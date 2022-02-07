from django import forms
from phonenumber_field.formfields import PhoneNumberField

from sales.enums import get_exp_year_choices, get_exp_month_choices
from sales.models import BaseReservation
from users.models import Customer


class PasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput())
    password_repeat = forms.CharField(widget=forms.PasswordInput())


class ReservationCustomerInfoForm(forms.ModelForm):

    confirmation_code = forms.CharField(widget=forms.HiddenInput())

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

    def __init__(self, *args, reservation=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['confirmation_code'].initial = reservation.confirmation_code

    class Meta:
        model = Customer
        exclude = ('user',)
        # fields = '__all__'
