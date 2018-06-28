from django import forms
from django.forms import fields


DAY_OF_REPORT__CHOICES = (
    ("mon", "Monday"),
    ("tues", "Tuesday"),
    ("wed", "Wednesday"),
    ("thurs", "Thursday"),
    ("fri", "Friday"),
    ("sat", "Saturday"),
    ("sun", "Sunday"),
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
