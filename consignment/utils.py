import calendar
import datetime
import pytz

from django.conf import settings

from consignment.models import Consigner, ConsignmentReservation
from sales.models import Rental


class EventCalendar(calendar.HTMLCalendar):

    def __init__(self, year=None, month=None, consigner=None, vehicle=None, **kwargs):
        self.year = year
        self.month = month
        self.consigner = consigner
        self.vehicle = vehicle
        super().__init__(**kwargs)

    def formatday(self, day, weekday):
        """
        Return a day as a table cell.
        """
        if day == 0:
            # day outside month
            return '<td class="%s">&nbsp;</td>' % self.cssclass_noday
        focus_date = datetime.datetime(self.year, self.month, day)
        focus_date = pytz.timezone(settings.TIME_ZONE).localize(focus_date)
        rentals = Rental.objects.filter(out_at__lte=focus_date, back_at__gte=focus_date, vehicle__external_owner=self.consigner)
        consigner_reservations = ConsignmentReservation.objects.filter(out_at__lte=focus_date, back_at__gte=focus_date)
        if self.vehicle:
            rentals = rentals.filter(vehicle=self.vehicle)
            consigner_reservations = consigner_reservations.filter(vehicle=self.vehicle)
        classes = self.cssclasses[weekday]
        if rentals.exists():
            classes += ' rental'
        if consigner_reservations.exists():
            classes += ' reservation'
        return '<td class="%s">%d</td>' % (classes, day)

    def formatmonth(self, withyear=True):
        return super().formatmonth(self.year, self.month, withyear=withyear)
