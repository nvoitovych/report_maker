from django import template

register = template.Library()


@register.filter
def subtract_indexes(value, arg):
    if value == 0 and arg == 0:
        return 0
    return value - arg + 1
