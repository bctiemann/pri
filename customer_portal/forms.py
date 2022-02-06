from django import forms

from sales.models import BaseReservation
from users.models import Customer


class PasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput())
    password_repeat = forms.CharField(widget=forms.PasswordInput())


class ReservationCustomerInfoForm(forms.ModelForm):

    confirmation_code = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, reservation=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['confirmation_code'].initial = reservation.confirmation_code

    class Meta:
        model = Customer
        fields = '__all__'