import json
from django import template
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import Group
from django.db.models import Sum

register = template.Library()


@register.assignment_tag
def get_range(start, end):
    return (str(x) for x in range(start, end))


@register.filter
def json_loads(data):
    return json.loads(data)


@register.assignment_tag
def json_load_value(data, key):
    key = key.replace("column", "field")
    list = json.loads(data)
    if key in list:
        return list[key]
    return ''


@register.assignment_tag
def get_user_token(user_id):
    try:
        token = Token.objects.get(user_id=user_id)
    except Token.DoesNotExist:
        token = Token.objects.create(user_id=user_id)
    return token.key


@register.filter(name='has_group')
def has_group(user, group_name):
    try:
        group = Group.objects.get(name=group_name)
        return True if user and group in user.groups.all() else False
    except Group.DoesNotExist:
        return False


@register.filter(name='is_owner')
def is_owner(user, instance):
    try:
        if user == instance.owner:
            return True
    except Group.DoesNotExist:
        pass
    return False


@register.filter(name='multiply')
def multiply(value, arg):
    return value*arg


@register.filter(name='percentage')
def percentage(number, total):
    if number and total:
        return round((number*100.0)/total, 2)
    return 0


@register.filter(name='percentage_int')
def percentage_int(number, total):
    if number:
        return int(round((number*100.0)/total, 2))
    return 0


@register.filter(name='array_value')
def array_value(data, key):
    if key in data:
        return data[key]
    return ''


@register.filter(name='number_format')
def number_format(value):
    return "{:,}".format(value)


@register.assignment_tag
def to_display_indicator(selected_filters, cumulative_result):
    if not selected_filters:
        return True

    if selected_filters and cumulative_result == '0':
        return False

    return True


@register.assignment_tag
def get_indicator_unit(indicator, value):

    if not value:
        return '0'

    if indicator['measurement_type'] == 'percentage' or indicator['measurement_type'] == 'percentage_x':
        value = "{:,}".format(round(value * 100, 1))
        return '{} {}'.format(value, '%')

    if not indicator['units'] == 'm3':
        return "{:,}".format(int(value))

    return "{:,}".format(round(value, 1))


@register.assignment_tag
def get_indicator_diff_results(indicator, month=None):
    try:
        if not indicator:
            return 0

        if isinstance(indicator, int):
            from internos.activityinfo.models import Indicator
            indicator = Indicator.objects.get(id=indicator)

        cumulative_values = indicator.cumulative_values
        previous_month = str(int(month) - 1)
        current_month = str(month)
        p_month_value = 0
        c_month_value = 0

        if 'months' in cumulative_values:
            cumulative_values = cumulative_values.get('months')

            if current_month in cumulative_values:
                c_month_value = int(cumulative_values[current_month])

            if previous_month in cumulative_values:
                p_month_value = int(cumulative_values[previous_month])

        return c_month_value - p_month_value
    except Exception as ex:
        # print(ex)
        return 0


@register.assignment_tag
def get_indicator_cumulative(indicator, month=None, partner=None, gov=None):
    try:

        cumulative_values = indicator['cumulative_values']

        if partner and gov and not partner == '0' and not gov == '0':
            cumulative_values = cumulative_values.get('partners_govs')
            key = '{}-{}'.format(partner, gov)
            if key in cumulative_values:
                return get_indicator_unit(indicator, cumulative_values[key])

        if partner and not partner == '0' and 'partners' in cumulative_values:
            cumulative_values = cumulative_values.get('partners')
            if partner in cumulative_values:
                return get_indicator_unit(indicator, cumulative_values[partner])

        if gov and not gov == '0' and 'govs' in cumulative_values:
            cumulative_values = cumulative_values.get('govs')
            if gov in cumulative_values:
                return get_indicator_unit(indicator, cumulative_values[gov])

        if month and 'months' in cumulative_values:
            month = str(month)
            cumulative_values = cumulative_values.get('months')
            if month in cumulative_values:
                return get_indicator_unit(indicator, cumulative_values[month])

        return get_indicator_unit(indicator, 0)
    except Exception as ex:
        # print(ex)
        return get_indicator_unit(indicator, 0)


@register.assignment_tag
def get_indicator_live_cumulative(indicator, month=None, partner=None, gov=None):
    try:

        cumulative_values = indicator['cumulative_values_live']

        if partner and gov and not partner == '0' and not gov == '0':
            cumulative_values = cumulative_values.get('partners_govs')
            key = '{}-{}'.format(partner, gov)
            if key in cumulative_values:
                return get_indicator_unit(indicator, cumulative_values[key])

        if partner and not partner == '0' and 'partners' in cumulative_values:
            cumulative_values = cumulative_values.get('partners')
            if partner in cumulative_values:
                return get_indicator_unit(indicator, cumulative_values[partner])

        if gov and not gov == '0' and 'govs' in cumulative_values:
            cumulative_values = cumulative_values.get('govs')
            if gov in cumulative_values:
                return get_indicator_unit(indicator, cumulative_values[gov])

        if month and 'months' in cumulative_values:
            month = str(month)
            cumulative_values = cumulative_values.get('months')
            if month in cumulative_values:
                return get_indicator_unit(indicator, cumulative_values[month])

        return get_indicator_unit(indicator, 0)
    except Exception as ex:
        # print(ex)
        return get_indicator_unit(indicator, 0)



@register.assignment_tag
def get_indicator_achieved(indicator, month=None, partner=None, gov=None):
    try:
        cumulative_values = indicator['cumulative_values']

        if partner and gov and not partner == '0' and not gov == '0':
            cumulative_values = cumulative_values.get('partners_govs')
            key = '{}-{}'.format(partner, gov)
            if key in cumulative_values:
                return round((cumulative_values[key] * 100.0) / indicator['target'], 2)

        if partner and not partner == '0' and 'partners' in cumulative_values:
            cumulative_values = cumulative_values.get('partners')
            if partner in cumulative_values:
                return round((cumulative_values[partner] * 100.0) / indicator['target'], 2)

        if gov and not gov == '0' and 'govs' in cumulative_values:
            cumulative_values = cumulative_values.get('govs')
            if gov in cumulative_values:
                return round((cumulative_values[gov] * 100.0) / indicator['target'], 2)

        if month and 'months' in cumulative_values:
            month = str(month)
            cumulative_values = cumulative_values.get('months')
            if month in cumulative_values:
                return round((cumulative_values[month] * 100.0) / indicator['target'], 2)

        return 0
    except Exception as ex:
        # print(ex)
        return 0


@register.assignment_tag
def get_indicator_live_achieved(indicator, month=None, partner=None, gov=None):
    try:
        cumulative_values = indicator['cumulative_values_live']

        if partner and gov and not partner == '0' and not gov == '0':
            cumulative_values = cumulative_values.get('partners_govs')
            key = '{}-{}'.format(partner, gov)
            if key in cumulative_values:
                return round((cumulative_values[key] * 100.0) / indicator['target'], 2)

        if partner and not partner == '0' and 'partners' in cumulative_values:
            cumulative_values = cumulative_values.get('partners')
            if partner in cumulative_values:
                return round((cumulative_values[partner] * 100.0) / indicator['target'], 2)

        if gov and not gov == '0' and 'govs' in cumulative_values:
            cumulative_values = cumulative_values.get('govs')
            if gov in cumulative_values:
                return round((cumulative_values[gov] * 100.0) / indicator['target'], 2)

        if month and 'months' in cumulative_values:
            month = str(month)
            cumulative_values = cumulative_values.get('months')
            if month in cumulative_values:
                return round((cumulative_values[month] * 100.0) / indicator['target'], 2)

        return 0
    except Exception as ex:
        # print(ex)
        return 0


@register.assignment_tag
def get_indicator_hpm_data(ai_id, month=None):
    from internos.activityinfo.models import Indicator

    data = {
        'id': 0,
        'name': 0,
        'cumulative': 0,
        'last_report_changes': 0
    }

    try:
        cumulative = 0
        indicator = Indicator.objects.get(id=int(ai_id))
        if month == '2':
            cumulative_values = indicator.cumulative_values_hpm
        else:
            cumulative_values = indicator.cumulative_values

        values_hpm = indicator.values_hpm
        last_month = month - 1
        last_month_value = 0
        if last_month in values_hpm:
            last_month_value = values_hpm[last_month]

        if month and 'months' in cumulative_values:
            month = str(month)
            cumulative_values = cumulative_values.get('months')
            if month in cumulative_values:
                cumulative = cumulative_values[month]

        cumulative = "{:,}".format(round(cumulative), 1)
        cumulative = cumulative.replace('.0', '')

        last_report_changes = "{:,}".format(round(cumulative - last_month_value, 1))
        last_report_changes = last_report_changes.replace('.0', '')

        data = {
            'id': ai_id,
            'name': indicator.name,
            'cumulative': cumulative,
            'last_report_changes': last_report_changes
        }

        return data
    except Exception as ex:
        print(ex)
        return data


@register.assignment_tag
def get_sub_indicators_data(ai_id):
    from internos.activityinfo.models import Indicator

    indicators = {}
    try:
        indicators = Indicator.objects.filter(sub_indicators=ai_id).values(
            'id',
            'ai_id',
            'name',
            'master_indicator',
            'master_indicator_sub',
            'master_indicator_sub_sub',
            'individual_indicator',
            'explication',
            'awp_code',
            'measurement_type',
            'units',
            'target',
            'status_color',
            'status',
            'cumulative_values',
            'values_partners_gov',
            'values_partners',
            'values_gov',
            'values',
            'values_live',
            'values_gov_live',
            'values_partners_live',
            'values_partners_gov_live',
            'cumulative_values_live',
        ).distinct()

        return indicators
    except Exception as ex:
        # print(ex)
        return indicators


@register.assignment_tag
def get_indicator_value(indicator, month=None, partner=None, gov=None):
    try:
        if partner and gov and not partner == '0' and not gov == '0':
            key = "{}-{}-{}".format(month, partner, gov)
            return get_indicator_unit(indicator, indicator['values_partners_gov'][key])
        if partner and not partner == '0':
            key = "{}-{}".format(month, partner)
            return get_indicator_unit(indicator, indicator['values_partners'][key])
        if gov and not gov == '0':
            key = "{}-{}".format(month, gov)
            return get_indicator_unit(indicator, indicator['values_gov'][key])

        return get_indicator_unit(indicator, indicator['values'][str(month)])
    except Exception as ex:
        # print(ex)
        return get_indicator_unit(indicator, 0)


@register.assignment_tag
def get_indicator_live_value(indicator, month=None, partner=None, gov=None):
    try:
        if partner and gov and not partner == '0' and not gov == '0':
            key = "{}-{}-{}".format(month, partner, gov)
            return get_indicator_unit(indicator, indicator['values_partners_gov'][key])
        if partner and not partner == '0':
            key = "{}-{}".format(month, partner)
            return get_indicator_unit(indicator, indicator['values_partners'][key])
        if gov and not gov == '0':
            key = "{}-{}".format(month, gov)
            return get_indicator_unit(indicator, indicator['values_gov'][key])

        return get_indicator_unit(indicator,indicator['values'][str(month)])
    except Exception as ex:
        # print(ex)
        return get_indicator_unit(indicator, 0)

