from django import template
from django.conf import settings

register = template.Library()


@register.filter
def currency(value):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return value
    return f"{settings.CURRENCY_SYMBOL} {value:,.0f}"


@register.filter
def star_range(rating):
    try:
        rating = float(rating)
    except (TypeError, ValueError):
        rating = 0
    return range(int(round(rating)))


@register.filter
def empty_star_range(rating):
    try:
        rating = float(rating)
    except (TypeError, ValueError):
        rating = 0
    return range(5 - int(round(rating)))


@register.simple_tag
def multiply(a, b):
    try:
        return float(a) * float(b)
    except (TypeError, ValueError):
        return 0
