from django import forms
from django.utils.translation import gettext as _
from django.contrib.admin.widgets import AdminDateWidget
from django.forms.fields import DateField
from bootstrap_daterangepicker import widgets, fields


class DateRangeForm(forms.Form):
    # Date Range Fields
    date_range_normal = fields.DateRangeField()
    date_range_with_format = fields.DateRangeField(
        input_formats=['%d/%m/%Y'],
        widget=widgets.DateRangeWidget(
            format='%d/%m/%Y'
        )
    )
    date_range_clearable = fields.DateRangeField(clearable=True)
