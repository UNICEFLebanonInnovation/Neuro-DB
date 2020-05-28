import datetime
from django import forms
from dal import autocomplete
from django.db.models import Q, Sum
from django.forms.models import BaseInlineFormSet
from django.contrib.admin.widgets import FilteredSelectMultiple, RelatedFieldWidgetWrapper
from .models import Database, Indicator, IndicatorTag, Activity
from django.forms import widgets


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
    tag_focus = forms.ModelChoiceField(
        required=False,
        queryset=IndicatorTag.objects.filter(type='focus')
    )
    tag_disability = forms.ModelChoiceField(
        required=False,
        queryset=IndicatorTag.objects.filter(type='disability')
    )
    denominator_indicator = forms.ModelChoiceField(
         required=False,
         queryset=Indicator.objects.none()
         # queryset=Indicator.objects.filter(master_indicator_sub=True)
    )
    numerator_indicator = forms.ModelChoiceField(
         required=False,
         queryset=Indicator.objects.none()
         # queryset=Indicator.objects.filter(master_indicator_sub=True)
    )
    sub_indicators = forms.ModelMultipleChoiceField(
        required=False,
        queryset=Indicator.objects.none(),
        widget=FilteredSelectMultiple('indicator', is_stacked=False)
    )
    summation_sub_indicators = forms.ModelMultipleChoiceField(
        required=False,
        queryset=Indicator.objects.none(),
        widget=FilteredSelectMultiple('indicator', is_stacked=False)
    )
    activity = forms.ModelChoiceField(
        required=False,
        queryset=Activity.objects.filter(database__reporting_year__year=datetime.datetime.now().year),
        # queryset=Activity.objects.none(),
        widget=widgets.Select(attrs={'style': 'height:200px;', 'size': '100px;'})
    )
    second_activity = forms.ModelChoiceField(
        required=False,
        queryset=Activity.objects.filter(database__reporting_year__year=datetime.datetime.now().year),
        # queryset=Activity.objects.none(),
        widget=autocomplete.ModelSelect2(url='activity_autocomplete')
    )
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

        if self.instance and hasattr(self.instance, 'activity') and self.instance.activity and \
           hasattr(self.instance, 'second_activity') and self.instance.second_activity:
            queryset = Indicator.objects.filter(
               Q(activity__database_id=self.instance.activity.database_id) |
               Q(activity__database_id=self.instance.second_activity.database_id)
               # Q(second_activity__database_id=self.instance.second_activity.database_id)
            )

        elif self.instance and hasattr(self.instance, 'activity') and self.instance.activity:
            queryset = Indicator.objects.filter(
               activity__database_id=self.instance.activity.database_id
            )
        else:
            queryset = Indicator.objects.none()
        self.fields['denominator_indicator'].queryset = queryset
        self.fields['numerator_indicator'].queryset = queryset
        self.fields['sub_indicators'].queryset = queryset
        self.fields['summation_sub_indicators'].queryset = queryset
        # self.fields['activity'].queryset = Activity.objects.filter(database__reporting_year__current=True)
        # self.fields['denominator_summation'].queryset = queryset
        # self.fields['numerator_summation'].queryset = queryset

