from datetime import datetime

from django import forms
from django.utils.translation import gettext as _
from django.contrib.admin.widgets import AdminDateWidget
from django.forms import fields


class DateRangeForm(forms.Form):
    start_date = fields.DateField(widget=forms.DateInput(attrs={
        'placeholder': 'DD/MM/YYYY',
        'class': 'date-input',
    }))
    end_date = fields.DateField(widget=forms.DateInput(attrs={
        'placeholder': 'DD/MM/YYYY',
        'class': 'date-input',
    }))


    """
        start_date = DateField(widget=forms.SelectDateWidget(attrs={
        'placeholder': 'DD/MM/YYYY',
        'class': 'date-input',
    }))
    end_date = DateField(widget=forms.SelectDateWidget(attrs={
        'placeholder': 'DD/MM/YYYY',
        'class': 'date-input',
    }))
    """
