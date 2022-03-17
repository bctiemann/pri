import re
from django import template

register = template.Library()


@register.filter
def mask_cc_number(cc_number):
    return re.sub('[0-9]', 'X', cc_number[0:-4]) + cc_number[-4:]
