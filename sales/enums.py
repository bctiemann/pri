from enum import Enum


class ReservationType(Enum):
    RENTAL = 'rental'
    PERFORMANCE_EXPERIENCE = 'perfexp'
    JOY_RIDE = 'joyride'


RESERVATION_TYPE_CODE_MAP = {
    ReservationType.RENTAL.value: 'P',
    ReservationType.PERFORMANCE_EXPERIENCE.value: 'X',
    ReservationType.JOY_RIDE.value: 'Y',
}
