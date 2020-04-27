from django import forms

from .models import EconomicReporting
from django.contrib.admin.widgets import AdminDateWidget

# from suit.widgets import SuitDateWidget, SuitTimeWidget, SuitSplitDateTimeWidget


class EconomicReportingForm(forms.ModelForm):

    # reporting_date = forms.DateField(widget=forms.SelectDateWidget(empty_label="Nothing"))
    reporting_date = forms.DateField(widget=AdminDateWidget())

    class Meta:
        model = EconomicReporting
        fields = '__all__'
