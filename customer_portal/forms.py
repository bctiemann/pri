from django import forms

from sales.models import BaseReservation
from users.models import Customer


class PasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput())
    password_repeat = forms.CharField(widget=forms.PasswordInput())


class ReservationCustomerInfoForm(forms.ModelForm):

    class Meta:
        model = Customer
        fields = '__all__'
