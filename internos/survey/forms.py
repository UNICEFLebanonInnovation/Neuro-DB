from django import forms

from .models import EconomicReporting
# from suit.widgets import SuitDateWidget, SuitTimeWidget, SuitSplitDateTimeWidget


class EconomicReportingForm(forms.ModelForm):

    reporting_date = forms.DateField(widget=forms.SelectDateWidget(empty_label="Nothing"))

    class Meta:
        model = EconomicReporting
        fields = '__all__'
