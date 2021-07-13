import datetime
import pytz

from django.conf import settings
from django import forms
from django.utils import timezone
from django.utils.translation import gettext_lazy as _, ngettext_lazy

from sales.models import Reservation


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
    DATETIME_FORMAT = '%m/%d/%Y %H:%M'

    out_date = forms.DateField()
    out_time = forms.TimeField(widget=forms.Select(choices=TIME_CHOICES))
    out_at = forms.DateTimeField(required=False)
    back_date = forms.DateField()
    back_time = forms.TimeField(widget=forms.Select(choices=TIME_CHOICES))
    back_at = forms.DateTimeField(required=False)
    drivers = forms.ChoiceField(choices=DRIVERS_CHOICES)
    delivery_required = forms.ChoiceField(choices=DELIVERY_CHOICES)

    def is_valid(self):
        return super().is_valid()

    def clean_out_at(self):
        try:
            date_str = f'{self.data["out_date"]} {self.data["out_time"]}'
            out_at = datetime.datetime.strptime(date_str, self.DATETIME_FORMAT)
        except ValueError:
            raise forms.ValidationError(_('Invalid out date.'))
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
            raise forms.ValidationError(_('Invalid back date.'))
        back_at = pytz.timezone(settings.TIME_ZONE).localize(back_at)
        if back_at < out_at:
            raise forms.ValidationError(_("You've specified a return date earlier than the rental date."))
        return back_at

    class Meta:
        model = Reservation
        fields = '__all__'
