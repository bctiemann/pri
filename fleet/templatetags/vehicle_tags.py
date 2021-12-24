from django import template

register = template.Library()


@register.filter
def multi_day_discounted_price(vehicle, num_days):
    return vehicle.get_multi_day_discounted_price(num_days)


@register.filter
def multi_day_miles_included(vehicle, num_days):
    return vehicle.get_multi_day_miles_included(num_days)
