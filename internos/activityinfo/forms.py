from django import forms
from .models import Database, Indicator, IndicatorTag


class DatabaseForm(forms.ModelForm):

    class Meta:
        model = Database
        fields = '__all__'


class IndicatorForm(forms.ModelForm):
    tag_gender = forms.ModelChoiceField(
        required=False,
        queryset=IndicatorTag.objects.filter(type='gender')
    )
    tag_age = forms.ModelChoiceField(
        required=False,
        queryset=IndicatorTag.objects.filter(type='age')
    )
    tag_nationality = forms.ModelChoiceField(
        required=False,
        queryset=IndicatorTag.objects.filter(type='nationality')
    )

    tag_disability = forms.ModelChoiceField(
        required=False,
        queryset=IndicatorTag.objects.filter(type='disability')
    )

    class Meta:
        model = Indicator
        fields = '__all__'
