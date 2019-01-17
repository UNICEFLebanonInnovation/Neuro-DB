from django import forms
from django.forms.models import BaseInlineFormSet
from .models import Database, Indicator, IndicatorTag


class DatabaseForm(forms.ModelForm):

    class Meta:
        model = Database
        fields = '__all__'


class IndicatorFormSet(BaseInlineFormSet):
    def get_form_kwargs(self, index):
        kwargs = super(IndicatorFormSet, self).get_form_kwargs(index)
        kwargs['parent_object'] = self.instance
        return kwargs


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
    denominator_indicator = forms.ModelChoiceField(
        required=False,
        queryset=Indicator.objects.all()
    )
    numerator_indicator = forms.ModelChoiceField(
        required=False,
        queryset=Indicator.objects.all()
    )

    class Meta:
        model = Indicator
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        """
        Only show supply items already in the supply plan
        """
        if 'instance' in kwargs:
            self.instance = kwargs['instance']

        super(IndicatorForm, self).__init__(*args, **kwargs)

        if self.instance and self.instance.activity:
            self.fields['denominator_indicator'].queryset = Indicator.objects.filter(
                activity__database_id=self.instance.activity.database_id)
            self.fields['numerator_indicator'].queryset = Indicator.objects.filter(
                activity__database_id=self.instance.activity.database_id)

