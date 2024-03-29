import logging
from enum import Enum
from datetime import datetime, time, timedelta

from django.conf import settings
from django.utils import timezone
from django.db import models
from django.db.utils import OperationalError, ProgrammingError

from fleet.models import Vehicle, VehicleMarketing, VehicleType

logger = logging.getLogger(__name__)


TRUE_FALSE_CHOICES = (
    (True, 'Yes'),
    (False, 'No')
)

DELIVERY_REQUIRED_CHOICES = (
    (False, 'Pickup at PRI'),
    (True, 'Delivery'),
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
        iter_dt = timezone.now().replace(month=month, day=1)
        label = iter_dt.strftime('%B (%m)')
        month_choices.append((iter_dt.strftime('%m'), label))
    if allow_null:
        month_choices = [(None, '------')] + month_choices
    return month_choices


def get_exp_year_choices(since_founding=False, allow_null=False, null_display_value='----'):
    start_year = current_year
    if since_founding:
        start_year = settings.COMPANY_FOUNDING_YEAR
    choices = [(year, year) for year in range(start_year, current_year + 11)]
    if allow_null:
        choices = [(None, null_display_value)] + choices
    return choices


def get_vehicle_choices(allow_null=False, null_display_value='----'):
    vehicle_choices = []
    try:
        vehicle_choices.append(('Cars', list((v.id, v.vehicle_name) for v in Vehicle.objects.filter(vehicle_type=VehicleType.CAR))))
        vehicle_choices.append(('Motorcycles', list((v.id, v.vehicle_name) for v in Vehicle.objects.filter(vehicle_type=VehicleType.BIKE))))
    except (OperationalError, ProgrammingError):
        logger.debug('Warning: DB tables not populated yet.')
    if allow_null:
        vehicle_choices = [(None, null_display_value)] + vehicle_choices
    return vehicle_choices


def get_extra_miles_choices():
    return ((k, v['label']) for k, v in settings.EXTRA_MILES_PRICES.items())


def get_numeric_choices(min_val, max_val):
    return ((v, v) for v in range(min_val, max_val + 1))


class ServiceType(models.TextChoices):
    RENTAL = ('rental', 'Rental')
    PERFORMANCE_EXPERIENCE = ('perfexp', 'Performance Experience')
    JOY_RIDE = ('joyride', 'Joy Ride')
    GIFT_CERTIFICATE = ('giftcert', 'Gift Certificate')
    AD_HOC_PAYMENT = ('subpay', 'Ad-hoc Payment')


SERVICE_TYPE_CODE_MAP = {
    ServiceType.RENTAL.value: 'P',
    ServiceType.PERFORMANCE_EXPERIENCE.value: 'X',
    ServiceType.JOY_RIDE.value: 'Y',
    ServiceType.AD_HOC_PAYMENT: 'Q',
}

CC_ERROR_PARAM_MAP = {
    'number': 'cc_number',
    'exp_month': 'cc_exp_mo',
    'exp_year': 'cc_exp_yr',
    'cvc': 'cc_cvv',
}

CC2_ERROR_PARAM_MAP = {
    'number': 'cc2_number',
    'exp_month': 'cc2_exp_mo',
    'exp_year': 'cc2_exp_yr',
    'cvc': 'cc2_cvv',
}