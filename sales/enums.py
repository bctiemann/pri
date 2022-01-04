from enum import Enum
from datetime import datetime, time, timedelta

from django.conf import settings
from django.utils import timezone

from fleet.models import VehicleMarketing, VehicleType


TRUE_FALSE_CHOICES = (
    (True, 'Yes'),
    (False, 'No')
)

current_year = timezone.now().year
birth_years = range(current_year - 18, current_year - 100, -1)
operational_years = range(settings.COMPANY_FOUNDING_YEAR, current_year + 10)


def get_service_hours():
    iter_dt = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today = iter_dt.date()
    service_start_time = time(hour=7, minute=0)
    service_end_time = time(hour=20, minute=0)
    service_hours = []

    while iter_dt.date() == today:
        iter_dt += timedelta(seconds=60 * 30)
        if service_start_time <= iter_dt.time() <= service_end_time:
            minute_suffix = iter_dt.strftime('%M %p').lower()
            service_hours.append((iter_dt.strftime('%H:%M'), f'{iter_dt.hour}:{minute_suffix}'))
    service_hours.append(('23:00', 'Other (Special)'))

    return service_hours


def get_exp_month_choices(allow_null=False):
    month_choices = []
    for month in range(1, 13):
        iter_dt = timezone.now().replace(month=month)
        label = iter_dt.strftime('%B (%m)')
        month_choices.append((iter_dt.strftime('%m'), label))
    if allow_null:
        month_choices = [(None, '------')] + month_choices
    return month_choices


def get_exp_year_choices(since_founding=False, allow_null=False):
    start_year = current_year
    if since_founding:
        start_year = settings.COMPANY_FOUNDING_YEAR
    choices = [(year, year) for year in range(start_year, current_year + 11)]
    if allow_null:
        choices = [(None, '----')] + choices
    return choices


def get_vehicle_choices():
    vehicle_choices = []
    vehicle_choices.append(('Cars', list((v.id, v.vehicle_name) for v in VehicleMarketing.objects.filter(vehicle_type=VehicleType.CAR))))
    vehicle_choices.append(('Motorcycles', list((v.id, v.vehicle_name) for v in VehicleMarketing.objects.filter(vehicle_type=VehicleType.BIKE))))
    return vehicle_choices


class ReservationType(Enum):
    RENTAL = 'rental'
    PERFORMANCE_EXPERIENCE = 'perfexp'
    JOY_RIDE = 'joyride'


RESERVATION_TYPE_CODE_MAP = {
    ReservationType.RENTAL.value: 'P',
    ReservationType.PERFORMANCE_EXPERIENCE.value: 'X',
    ReservationType.JOY_RIDE.value: 'Y',
}
