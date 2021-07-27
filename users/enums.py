from enum import Enum


class AdminIdleTimeCSSClass(Enum):
    LESS_THAN_1_HOUR = 'less-than-1-hour'
    LESS_THAN_2_DAYS = 'less-than-2-days'
    MORE_THAN_2_DAYS = 'more-than-2-days'
