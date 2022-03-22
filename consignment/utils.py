import calendar
import datetime
import pytz
from dateutil.relativedelta import relativedelta

from django.conf import settings
from django.utils import timezone

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

        # Filter rentals/reservations down to the current (localized) date, without hitting the DB again
        rentals = set(filter(lambda r: r.out_date <= focus_date.date() <= r.back_date, self.rentals))
        consigner_reservations = set(filter(lambda r: r.out_date <= focus_date.date() <= r.back_date, self.consigner_reservations))

        date_str = focus_date.strftime('%m/%d/%Y')
        classes = self.cssclasses[weekday]
        reservation_id_str = ''
        if focus_date.date() == timezone.now().astimezone(pytz.timezone(settings.TIME_ZONE)).date():
            classes += ' today'
        if rentals:
            classes += ' rental'
        if consigner_reservations:
            classes += ' reservation'
            reservation_id_str = 'reservationid="%s"' % ','.join([str(r.id) for r in consigner_reservations])
        return '<td class="%s" date="%s" %s><div class="day-label">%d</div></td>' % (classes, date_str, reservation_id_str, day)

    def formatmonth(self, withyear=True):
        month_start = datetime.datetime(self.year, self.month, 1)
        month_start = pytz.timezone(settings.TIME_ZONE).localize(month_start)
        next_month_start = month_start + relativedelta(months=1)

        # Get filtered rentals and reservations which are relevant for the selected month
        self.rentals = Rental.objects.filter(out_at__lte=next_month_start, back_at__gte=month_start)
        self.rentals = self.rentals.filter(vehicle__external_owner=self.consigner)
        self.consigner_reservations = ConsignmentReservation.objects.filter(out_at__lte=next_month_start, back_at__gte=month_start)
        self.consigner_reservations = self.consigner_reservations.filter(consigner=self.consigner)
        if self.vehicle:
            self.rentals = self.rentals.filter(vehicle=self.vehicle)
            self.consigner_reservations = self.consigner_reservations.filter(vehicle=self.vehicle)

        return super().formatmonth(self.year, self.month, withyear=withyear)
