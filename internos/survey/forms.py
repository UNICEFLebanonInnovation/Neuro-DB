import datetime

from django import forms
from .models import EconomicReporting, MonitoringReporting
from django.contrib.admin.widgets import AdminDateWidget

# from suit.widgets import SuitDateWidget, SuitTimeWidget, SuitSplitDateTimeWidget


class EconomicReportingForm(forms.ModelForm):

    # reporting_date = forms.DateField(widget=forms.SelectDateWidget(empty_label="Nothing"))
    reporting_date = forms.DateField(widget=AdminDateWidget())

    class Meta:
        model = EconomicReporting
        fields = '__all__'


class MonitoringReportingForm(forms.ModelForm):

    # reporting_date = forms.DateField(widget=forms.SelectDateWidget(empty_label="Nothing"))
    reporting_date = forms.DateField(widget=AdminDateWidget())

    class Meta:
        model = MonitoringReporting
        fields = '__all__'


BIRTH_YEAR_CHOICES = ['1980', '1981', '1982']
CURRENT_YEAR = datetime.datetime.now().year


class ResearchForm(forms.ModelForm):
    # publication_year = forms.DateField(widget=forms.SelectDateWidget(years=BIRTH_YEAR_CHOICES))
    publication_year = forms.ChoiceField(choices=list(((str(x), x) for x in range(CURRENT_YEAR - 5, CURRENT_YEAR + 5))),
                                         initial=CURRENT_YEAR)
