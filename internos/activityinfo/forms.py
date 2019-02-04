from django import forms
from django.forms.models import BaseInlineFormSet
from django.contrib.admin.widgets import FilteredSelectMultiple, RelatedFieldWidgetWrapper
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
         queryset=Indicator.objects.filter(master_indicator_sub=True)
    )
    numerator_indicator = forms.ModelChoiceField(
         required=False,
         queryset=Indicator.objects.filter(master_indicator_sub=True)
    )
    # sub_indicators = forms.ModelMultipleChoiceField(
    #     required=False,
    #     queryset=Indicator.objects.all(),
    #     widget=FilteredSelectMultiple('indicator', is_stacked=False)
    # )
    # summation_sub_indicators = forms.ModelMultipleChoiceField(
    #     required=False,
    #     queryset=Indicator.objects.all(),
    #     widget=FilteredSelectMultiple('indicator', is_stacked=False)
    # )
    # denominator_summation = forms.ModelMultipleChoiceField(
    #     required=False,
    #     queryset=Indicator.objects.all(),
    #     widget=FilteredSelectMultiple('indicator', is_stacked=False)
    # )
    # numerator_summation = forms.ModelMultipleChoiceField(
    #     required=False,
    #     queryset=Indicator.objects.all(),
    #     widget=FilteredSelectMultiple('indicator', is_stacked=False)
    # )

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

     #   if self.instance and self.instance.activity:
      #      queryset = Indicator.objects.filter(
       #         activity__database_id=self.instance.activity.database_id)
            # self.fields['denominator_indicator'].queryset = queryset
            # self.fields['numerator_indicator'].queryset = queryset
            # self.fields['sub_indicators'].queryset = queryset
            # self.fields['summation_sub_indicators'].queryset = queryset
            # self.fields['denominator_summation'].queryset = queryset
            # self.fields['numerator_summation'].queryset = queryset

