from datetime import datetime, timedelta
from django import template

register = template.Library()


@register.filter
def date_n_days_ago_filter(date, n):
    date_n_days_ago = date - timedelta(days=n)
    return date_n_days_ago
