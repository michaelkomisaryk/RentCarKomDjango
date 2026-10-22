from django import template
from django.utils.translation import gettext

from fleet.currency import format_money

register = template.Library()


@register.filter
def money(amount):
    return format_money(amount)


@register.filter
def tr(value):
    if value in (None, ""):
        return ""
    return gettext(str(value))
