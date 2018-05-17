from django import forms
from django.forms import fields


DAY_OF_REPORT__CHOICES = (
    ("mon", "Понеділок"),
    ("tues", "Вівторок"),
    ("wed", "Середа"),
    ("thurs", "Четвер"),
    ("fri", "П'ятниця"),
    ("sat", "Субота"),
    ("sun", "Неділя"),
)


class CustomReportForm(forms.Form):
    start_date = fields.DateField(widget=forms.DateInput(attrs={
        'placeholder': 'DD/MM/YYYY',
        'class': 'date-input',
    }))
    end_date = fields.DateField(widget=forms.DateInput(attrs={
        'placeholder': 'DD/MM/YYYY',
        'class': 'date-input',
    }))
    day_of_report = fields.ChoiceField(
        choices=DAY_OF_REPORT__CHOICES,
    )

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
