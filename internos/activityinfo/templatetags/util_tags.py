import json
import datetime
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
    return value * arg


@register.filter(name='percentage')
def percentage(number, total):
    if number and total:
        return round((number * 100.0) / total, 2)
    return 0


@register.filter(name='percentage_int')
def percentage_int(number, total):
    if number:
        return int(round((number * 100.0) / total, 2))
    return 0


@register.filter(name='percentage_float')
def percentage_float(number, total):
    try:
        if number and not isinstance(total, dict):
            return float(round((float(number) * 100.0) / float(total), 2))
        return 0
    except Exception:
        return 0


@register.filter(name='array_value')
def array_value(data, key):
    if key in data:
        return data[key]
    return ''


@register.filter(name='number_format')
def number_format(value):
    try:
        return "{:,}".format(int(value))
    except Exception:
        return value


@register.assignment_tag
def get_current_year():
    from datetime import date
    return date.today().year


@register.assignment_tag
def to_display_indicator(selected_filters, cumulative_result):
    if not selected_filters:
        return True

    if selected_filters and (cumulative_result == '0' or cumulative_result == 0):
        return False

    return True


@register.assignment_tag
def check_indicators_unit(indicators, cumulative_value):
    if not cumulative_value:
        return '0'
    for indicator in indicators:
        if indicator['measurement_type'] == 'percentage' or indicator['measurement_type'] == 'percentage_x':
            return '{} {}'.format(cumulative_value, '%')
        if not indicator['units'] == 'm3':
            return "{:,}".format(int(cumulative_value))

    return "{:,}".format(0)


@register.assignment_tag
def get_indicator_unit(indicator, value):
    if not value:
        return '0'
    if indicator['measurement_type'] == 'percentage':
        return '{} {}'.format(round(value, 1), '%')

    if indicator['measurement_type'] == 'percentage_x':
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
        value = 0
        cumulative_values = indicator['cumulative_values']

        if partner and gov and not gov == '0':
            cumulative_values = cumulative_values.get('partners_govs')
            for par in partner:
                key = '{}-{}'.format(gov, par)
                if key in cumulative_values:
                    value += cumulative_values[key]
            return get_indicator_unit(indicator, value)

        if partner and 'partners' in cumulative_values:
            cumulative_values = cumulative_values.get('partners')
            for par in partner:
                if par in cumulative_values:
                    value += cumulative_values[par]
            return get_indicator_unit(indicator, value)

        if gov and 'govs' in cumulative_values:
            cumulative_values = cumulative_values.get('govs')
            for gv in gov:
                if gv in cumulative_values:
                    value += cumulative_values[gv]
            return get_indicator_unit(indicator, value)

        if gov and not gov == '0' and 'govs' in cumulative_values:
            cumulative_values = cumulative_values.get('govs')
            if gov in cumulative_values:
                return get_indicator_unit(indicator, cumulative_values[gov])

        if 'months' in cumulative_values:
            return get_indicator_unit(indicator, cumulative_values.get('months'))

        return get_indicator_unit(indicator, 0)
    except Exception as ex:
        print(ex)
        return get_indicator_unit(indicator, 0)


@register.assignment_tag
def get_indicator_cumulative_months(indicator, month=None, partner=None, gov=None):
    try:
        value = 0
        cumulative_values = indicator['cumulative_values']
        if partner and gov and month:
            cumulative_values = cumulative_values.get('partners_govs')  # @todo variable not used
            for par in partner:
                for g in gov:
                    for m in month:
                        key = "{}-{}-{}".format(m, g, par)
                        value += indicator['values_partners_gov'][key]
            return get_indicator_unit(indicator, value)

        if partner and gov and not month:
            cumulative_values = cumulative_values.get('partners_govs')
            for par in partner:
                for g in gov:
                    key = "{}-{}".format(g, par)
                    if key in cumulative_values:
                        value += cumulative_values[key]
            return get_indicator_unit(indicator, value)

        if partner and month and not gov:
            cumulative_values = cumulative_values.get('partners')  # @todo variable not used
            if type(partner) == unicode:
                for m in month:
                    key = "{}-{}".format(m, partner)
                    value += indicator['values_partners'][key]
                return get_indicator_unit(indicator, value)
            else:
                for par in partner:
                    for m in month:
                        key = "{}-{}".format(m, par)
                        value += indicator['values_partners'][key]
                return get_indicator_unit(indicator, value)

        if gov and month and not partner:
            cumulative_values = cumulative_values.get('govs')  # @todo variable not used
            if type(gov) == unicode:
                for m in month:
                    key = "{}-{}".format(m, gov)
                    value += indicator['values_gov'][key]
                return get_indicator_unit(indicator, value)
            else:
                for g in gov:
                    for m in month:
                        key = "{}-{}".format(m, g)
                        value += indicator['values_gov'][key]
                return get_indicator_unit(indicator, value)

        if partner and 'partners' in cumulative_values:
            cumulative_values = cumulative_values.get('partners')
            for par in partner:
                if par in cumulative_values:
                    value += cumulative_values[par]
            return get_indicator_unit(indicator, value)

        if gov and 'govs' in cumulative_values:
            cumulative_values = cumulative_values.get('govs')
            for gv in gov:
                if gv in cumulative_values:
                    value += cumulative_values[gv]
            return get_indicator_unit(indicator, value)

        if month and indicator['values']:
            for i in month:
                if str(i) in indicator['values']:
                    value = value + float(indicator['values'][str(i)])
            return get_indicator_unit(indicator, value)

        if cumulative_values and 'months' in cumulative_values:
            return get_indicator_unit(indicator, cumulative_values.get('months'))

        return get_indicator_unit(indicator, 0)

    except Exception as ex:
        # print('error ' + ex.message)
        return get_indicator_unit(indicator, 0)


@register.assignment_tag
def get_indicator_partner_cumulative(indicator, partner=None, gov=None):
    try:
        value = 0
        cumulative_values = indicator['cumulative_values']
        if partner and gov and not gov == '0':
            cumulative_values = cumulative_values.get('partners_govs')
            key = '{}-{}'.format(gov, partner)
            if key in cumulative_values:
                value += cumulative_values[key]
            return get_indicator_unit(indicator, value)
        if partner and 'partners' in cumulative_values:
            cumulative_values = cumulative_values.get('partners')
            if partner in cumulative_values:
                value += cumulative_values[partner]
            return get_indicator_unit(indicator, value)

        if gov and 'govs' in cumulative_values:
            cumulative_values = cumulative_values.get('govs')
            if gov in cumulative_values:
                value += cumulative_values[gov]
        return get_indicator_unit(indicator, value)
    except Exception as ex:
        # print('error ' + ex.message)
        return get_indicator_unit(indicator, 0)


@register.assignment_tag
def get_indicators_partner_cumulative(indicator, partner=None, gov=None):
    value = 0
    try:
        for ind in indicator:
            cumulative_values = ind['cumulative_values']
            if partner and gov and not gov == '0':
                cumulative_values = cumulative_values.get('partners_govs')
                key = '{}-{}'.format(gov, partner)
                if key in cumulative_values:
                    value += cumulative_values[key]

            if partner and 'partners' in cumulative_values:
                cumulative_values = cumulative_values.get('partners')
                if partner in cumulative_values:
                    value += cumulative_values[partner]

            if gov and 'govs' in cumulative_values:
                cumulative_values = cumulative_values.get('govs')
                if gov in cumulative_values:
                    value += cumulative_values[gov]
        return check_indicators_unit(indicator, value)

    except Exception as ex:
        # print('error ' + ex.message)
        return 0


@register.assignment_tag
def get_indicator_cumulative_sector(indicator, month=None, partner=None, site=None):
    try:
        value = 0
        cumulative_values = indicator['cumulative_values_sector']
        if partner and site and month:
            for par in partner:
                for s in site:
                    for m in month:
                        key = "{}-{}-{}".format(m, s, par)
                        value += indicator['partners_sites_sector'][key]
            return get_indicator_unit(indicator, value)
        if partner and site and not month:
            cumulative_values = cumulative_values.get('partners_sites')
            for par in partner:
                for s in site:
                    key = "{}-{}".format(s, par)
                    if key in cumulative_values:
                        value += cumulative_values[key]
            return get_indicator_unit(indicator, value)

        if partner and month and not site:
            if type(partner) == unicode:
                for m in month:
                    key = "{}-{}".format(m, partner)
                    value += indicator['values_partners_sector'][key]
                return get_indicator_unit(indicator, value)
            else:
                for par in partner:
                    for m in month:
                        key = "{}-{}".format(m, par)
                        value += indicator['values_partners_sector'][key]
                return get_indicator_unit(indicator, value)

        if site and month and not partner:
            if type(site) == unicode:
                for m in month:
                    key = "{}-{}".format(m, site)
                    value += indicator['values_sites_sector'][key]
                return get_indicator_unit(indicator, value)
            else:
                for s in site:
                    for m in month:
                        key = "{}-{}".format(m, s)
                        value += indicator['values_sites_sector'][key]
                return get_indicator_unit(indicator, value)

        if partner and 'partners' in cumulative_values:
            cumulative_values = cumulative_values.get('partners')
            for par in partner:
                if par in cumulative_values:
                    value += cumulative_values[par]
            return get_indicator_unit(indicator, value)

        if site and 'sites' in cumulative_values:
            cumulative_values = cumulative_values.get('sites')
            for s in site:
                if s in cumulative_values:
                    value += cumulative_values[s]
            return get_indicator_unit(indicator, value)

        if month and indicator['values_sector']:
            for i in month:
                if str(i) in indicator['values_sector']:
                    value = value + float(indicator['values_sector'][str(i)])
            return get_indicator_unit(indicator, value)

        if cumulative_values and 'months' in cumulative_values:
            return get_indicator_unit(indicator, cumulative_values.get('months'))

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
            key = '{}-{}'.format(gov, partner)
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

        if 'months' in cumulative_values:
            return get_indicator_unit(indicator, cumulative_values.get('months'))

        # if month and 'months' in cumulative_values:
        #     month = str(month)
        #     cumulative_values = cumulative_values.get('months')
        #     if month in cumulative_values:
        #         return get_indicator_unit(indicator, cumulative_values[month])

        return get_indicator_unit(indicator, 0)
    except Exception as ex:
        # print(ex)
        return get_indicator_unit(indicator, 0)


def calculate_achievement(indicator, cumulative_values, target, month=None, partner=None, gov=None):
    try:

        if not target:
            return 0

        value = 0

        if partner and gov and not gov == '0':
            cumulative_values = cumulative_values.get('partners_govs')
            for par in partner:
                key = '{}-{}'.format(gov, par)
                if key in cumulative_values:
                    value += cumulative_values[key]
            return round((value * 100.0) / target, 2)

        if partner and 'partners' in cumulative_values:
            cumulative_values = cumulative_values.get('partners')
            for par in partner:
                if par in cumulative_values:
                    value += cumulative_values[par]
                return round((value * 100.0) / target, 2)

        if gov and 'govs' in cumulative_values:
            cumulative_values = cumulative_values.get('govs')
            for gv in gov:
                if gv in cumulative_values:
                    value += cumulative_values[gv]
                return round((value * 100.0) / target, 2)

        if gov and not gov == '0' and 'govs' in cumulative_values:
            cumulative_values = cumulative_values.get('govs')
            if gov in cumulative_values:
                return round((cumulative_values[gov] * 100.0) / target, 2)

        if 'months' in cumulative_values:
            return round((cumulative_values['months'] * 100.0) / target, 2)

        return 0
    except Exception as ex:
        # print(ex)
        return 0


@register.assignment_tag
def get_indicator_achieved_sector(indicator, month=None, partner=None, gov=None):
    return calculate_achievement(indicator, indicator['cumulative_values_sector'], indicator['target_sector'],
                                 month=month, partner=partner, gov=gov)


@register.assignment_tag
def get_indicator_achieved(indicator, month=None, partner=None, gov=None):
    return calculate_achievement(indicator, indicator['cumulative_values'], indicator['target'], month=month,
                                 partner=partner, gov=gov)
    #
    # try:
    #     cumulative_values = indicator['cumulative_values']
    #
    #     if not indicator['target']:
    #         return 0
    #
    #     value = 0
    #
    #     if partner and gov and not gov == '0':
    #         cumulative_values = cumulative_values.get('partners_govs')
    #         for par in partner:
    #             key = '{}-{}'.format(gov, par)
    #             if key in cumulative_values:
    #                 value += cumulative_values[key]
    #         return round((value * 100.0) / indicator['target'], 2)
    #
    #     if partner and 'partners' in cumulative_values:
    #         cumulative_values = cumulative_values.get('partners')
    #         for par in partner:
    #             if par in cumulative_values:
    #                 value += cumulative_values[par]
    #             return round((value * 100.0) / indicator['target'], 2)
    #
    #     if gov and not gov == '0' and 'govs' in cumulative_values:
    #         cumulative_values = cumulative_values.get('govs')
    #         if gov in cumulative_values:
    #             return round((cumulative_values[gov] * 100.0) / indicator['target'], 2)
    #
    #     if 'months' in cumulative_values:
    #         return round((cumulative_values['months'] * 100.0) / indicator['target'], 2)
    #
    #     return 0
    # except Exception as ex:
    #     # print(ex)
    #     return 0


@register.assignment_tag
def get_indicator_live_achieved(indicator, month=None, partner=None, gov=None):
    try:
        cumulative_values = indicator['cumulative_values_live']

        if not indicator['target']:
            return 0

        if partner and gov and not partner == '0' and not gov == '0':
            cumulative_values = cumulative_values.get('partners_govs')
            key = '{}-{}'.format(gov, partner)
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

        if 'months' in cumulative_values:
            return round((cumulative_values['months'] * 100.0) / indicator['target'], 2)

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
        'last_report_changes': 0,
        'boys': 0,
        'girls': 0,
        'male': 0,
        'female': 0,
        'leb': 0,
        'syr': 0,
        'prs': 0,
        'prl': 0,
        'oth': 0,
        'lebanese': 0,
        'non_lebanese': 0,
        'last_report_changes_leb': 0,
        'last_report_changes_syr': 0,
        'last_report_changes_prs': 0,
        'last_report_changes_prl': 0,
        'last_report_changes_oth': 0,
        'last_report_changes_lebanese': 0,
        'last_report_changes_non_lebanese': 0,
        'bln': 0,
        'cbece': 0,
        'alp': 0,
        # 'tag_programme_total': 0,
        'last_report_changes_bln': 0,
        'last_report_changes_cbece': 0,
        'last_report_changes_alp': 0,
    }

    try:
        indicator = Indicator.objects.get(id=int(ai_id))
    except Exception as ex:
        return data

    try:
        today = datetime.date.today()
        first = today.replace(day=1)
        last_month = first - datetime.timedelta(days=1)
        last_month_number = int(last_month.strftime("%m"))
        last_month_number = 12

        cumulative = 0
        if str(month) == str(last_month_number):
            cumulative_values = indicator.cumulative_values
        else:
            cumulative_values = indicator.cumulative_values_hpm

        values_hpm = indicator.values_hpm
        previous_month = int(month) - 1
        last_month_value = 0

        if str(previous_month) in indicator.cumulative_values_hpm['months']:
            last_month_value = indicator.cumulative_values_hpm['months'][str(previous_month)]

        if 'months' in cumulative_values:
            month = str(month)
            cumulative_values = cumulative_values.get('months')
            if isinstance(cumulative_values, dict):
                if month in cumulative_values:
                    cumulative = cumulative_values[month]
            else:
                cumulative = cumulative_values

        last_report_changes_bln = 0
        last_report_changes_cbece = 0
        last_report_changes_alp = 0

        tag_prog_bln = 0.0
        tag_prog_cbece = 0.0
        tag_prog_alp = 0.0

        last_report_changes_leb = 0
        last_report_changes_syr = 0
        last_report_changes_prs = 0
        last_report_changes_prl = 0
        last_report_changes_oth = 0

        tag_nath_leb = float(indicator.values_tags['LEB']) if 'LEB' in indicator.values_tags else 0.0
        tag_nath_syr = float(indicator.values_tags['SYR']) if 'SYR' in indicator.values_tags else 0.0
        tag_nath_prs = float(indicator.values_tags['PRS']) if 'PRS' in indicator.values_tags else 0.0
        tag_nath_prl = float(indicator.values_tags['PRL']) if 'PRL' in indicator.values_tags else 0.0
        tag_nath_oth = float(indicator.values_tags['OTH']) if 'OTH' in indicator.values_tags else 0.0

        if 'tags' in indicator.cumulative_values_hpm:
            month_value_tag = indicator.cumulative_values_hpm['tags']
            key1 = '{}-{}'.format(month, 'BLN')
            key2 = '{}-{}'.format(month, 'CBECE')
            key3 = '{}-{}'.format(month, 'ALP')
            if key1 in month_value_tag:
                tag_prog_bln = month_value_tag[key1]
            if key2 in month_value_tag:
                tag_prog_cbece = month_value_tag[key2]
            if key3 in month_value_tag:
                tag_prog_alp = month_value_tag[key3]

            key1 = '{}-{}'.format(month, 'LEB')
            key2 = '{}-{}'.format(month, 'SYR')
            key3 = '{}-{}'.format(month, 'PRS')
            key4 = '{}-{}'.format(month, 'PRL')
            key5 = '{}-{}'.format(month, 'OTH')
            if key1 in month_value_tag:
                tag_nath_leb = month_value_tag[key1]
            if key2 in month_value_tag:
                tag_nath_syr = month_value_tag[key2]
            if key3 in month_value_tag:
                tag_nath_prs = month_value_tag[key3]
            if key4 in month_value_tag:
                tag_nath_prl = month_value_tag[key4]
            if key5 in month_value_tag:
                tag_nath_oth = month_value_tag[key5]

        if 'tags' in indicator.cumulative_values_hpm:
            last_month_value_tag = indicator.cumulative_values_hpm['tags']
            key1 = '{}-{}'.format(previous_month, 'BLN')
            key2 = '{}-{}'.format(previous_month, 'CBECE')
            key3 = '{}-{}'.format(previous_month, 'ALP')
            if key1 in last_month_value_tag:
                last_report_changes_bln = tag_prog_bln - float(last_month_value_tag[key1])
            if key2 in last_month_value_tag:
                last_report_changes_cbece = tag_prog_cbece - float(last_month_value_tag[key2])
            if key3 in last_month_value_tag:
                last_report_changes_alp = tag_prog_alp - float(last_month_value_tag[key3])

            key1 = '{}-{}'.format(previous_month, 'LEB')
            key2 = '{}-{}'.format(previous_month, 'SYR')
            key3 = '{}-{}'.format(previous_month, 'PRS')
            key4 = '{}-{}'.format(previous_month, 'PRL')
            key5 = '{}-{}'.format(previous_month, 'OTH')
            if key1 in last_month_value_tag:
                last_report_changes_leb = tag_nath_leb - float(last_month_value_tag[key1])
            if key2 in last_month_value_tag:
                last_report_changes_syr = tag_nath_syr - float(last_month_value_tag[key2])
            if key3 in last_month_value_tag:
                last_report_changes_prs = tag_nath_prs - float(last_month_value_tag[key3])
            if key4 in last_month_value_tag:
                last_report_changes_prl = tag_nath_prl - float(last_month_value_tag[key4])
            if key5 in last_month_value_tag:
                last_report_changes_oth = tag_nath_oth - float(last_month_value_tag[key5])

        cumulative_result = "{:,}".format(round(cumulative), 1)
        cumulative_result = cumulative_result.replace('.0', '')

        if int(month) == 1:
            last_report_changes = 0
        else:
            last_report_changes = "{:,}".format(round(int(cumulative) - int(last_month_value), 1))
            # last_report_changes = "{:,}".format(round(abs(int(cumulative) - int(last_month_value)), 1))
            last_report_changes = last_report_changes.replace('.0', '')

        data = {
            'id': ai_id,
            'name': indicator.name,
            'cumulative': cumulative_result,
            'last_report_changes': last_report_changes,
            'boys': str(round(indicator.values_tags['boys'])).replace('.0',
                                                                      '') if 'boys' in indicator.values_tags else 0,
            'girls': str(round(indicator.values_tags['girls'])).replace('.0',
                                                                        '') if 'girls' in indicator.values_tags else 0,
            'male': str(round(indicator.values_tags['male'])).replace('.0',
                                                                      '') if 'male' in indicator.values_tags else 0,
            'female': str(round(indicator.values_tags['female'])).replace('.0',
                                                                          '') if 'female' in indicator.values_tags else 0,
            'bln': str("{:,}".format(round(tag_prog_bln))).replace('.0', ''),
            'cbece': str("{:,}".format(round(tag_prog_cbece))).replace('.0', ''),
            'alp': str("{:,}".format(round(tag_prog_alp))).replace('.0', ''),
            # 'tag_programme_total': tag_prog_bln + tag_prog_cbece + tag_prog_alp,
            'last_report_changes_bln': str("{:,}".format(last_report_changes_bln)).replace('.0', ''),
            'last_report_changes_cbece': str("{:,}".format(last_report_changes_cbece)).replace('.0', ''),
            'last_report_changes_alp': str("{:,}".format(last_report_changes_alp)).replace('.0', ''),
            'lebanese': str("{:,}".format(tag_nath_leb)).replace('.0', ''),
            'non_lebanese': str("{:,}".format(tag_nath_syr + tag_nath_prs + tag_nath_prl + tag_nath_oth)).replace('.0',
                                                                                                                  ''),
            'last_report_changes_lebanese': str("{:,}".format(last_report_changes_leb)).replace('.0', ''),
            'last_report_changes_non_lebanese': str("{:,}".format(last_report_changes_syr
                                                                  + last_report_changes_prs + last_report_changes_prl
                                                                  + last_report_changes_oth)).replace('.0', ''),
        }

        return data
    except Exception as ex:
        # print(ex.message)
        return data


@register.assignment_tag
def get_hpm_indicators(db_id, month=None):  # @todo variable month not used
    from internos.activityinfo.models import Indicator, Database

    db_indicators = {}
    db = Database.objects.get(id=db_id)
    indicators = Indicator.objects.filter(activity__database=db, hpm_indicator=True).order_by('sequence')
    indicators = indicators.values(
        'id',
        'ai_id',
        'name',
        'units',
        'target',
        'target_sector',
        'cumulative_values',
        'measurement_type',
        'values',
        'values_sector',
        'cumulative_values_sector'
    ).distinct()
    indicators = list(indicators)
    db_indicators[db.ai_id] = []
    db_indicators[db.ai_id].append(indicators)

    return db_indicators


@register.assignment_tag
def get_display_db(dict_indicators, db_id):
    for key, value in dict_indicators.items():
        if key == db_id:
            for indicator in value:
                if indicator:
                    return True
                else:
                    return False


@register.assignment_tag
def get_hpm_cumulative(indicator, month):
    try:
        value = 0
        if month > 1:
            for m in range(1, month):
                if indicator['values']:
                    if str(m) in indicator['values']:
                        value += float(indicator['values'][str(m)])
        return get_indicator_unit(indicator, value)
    except Exception as ex:
        return get_indicator_unit(indicator, value)


@register.assignment_tag
def get_hpm_cumulative_sector(indicator, month):
    value = 0
    try:
        if month > 1:
            for m in range(1, month):
                if indicator['values_sector']:
                    if str(m) in indicator['values_sector']:
                        value += float(indicator['values_sector'][str(m)])
        return get_indicator_unit(indicator, value)
    except Exception as ex:
        return get_indicator_unit(indicator, value)

@register.assignment_tag
def get_hpm_cumulative_change_sector(indicator, month):
    cumulative_value1 = 0
    cumulative_value2 = 0
    change_value = 0
    try:
        if month > 1:
            for m in range(1, month + 1):
                if indicator['values_sector']:
                    if str(m) in indicator['values_sector']:
                        cumulative_value1 += float(indicator['values_sector'][str(m)])
            for m in range(1, month):
                if indicator['values_sector']:
                    if str(m) in indicator['values_sector']:
                        cumulative_value2 += float(indicator['values_sector'][str(m)])

        change_value = cumulative_value1 - cumulative_value2
        return get_indicator_unit(indicator, change_value)
    except Exception as ex:
        return get_indicator_unit(indicator, change_value)


@register.assignment_tag
def get_hpm_cumulative_change(indicator, month):

    cumulative_value1 = 0
    cumulative_value2 = 0
    change_value = 0
    try:
        if month > 1:
            for m in range(1, month + 1):
                if str(m) in indicator['values']:
                    cumulative_value1 += float(indicator['values'][str(m)])
            for m in range(1, month):
                if str(m) in indicator['values']:
                    cumulative_value2 += float(indicator['values'][str(m)])

        change_value = cumulative_value1 - cumulative_value2
        return get_indicator_unit(indicator, change_value)
    except Exception as ex:
        return get_indicator_unit(indicator, change_value)



@register.assignment_tag
def get_sub_indicators_data(ai_id, is_sector=False):
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
            'target_sector',
            'status_color',
            'status_color_sector',
            'status',
            'status_sector',
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
            'values_tags',
            'cumulative_values_sector',
            'values_partners_sites_sector',
            'values_partners_sector',
            'values_sites_sector',
            'values_sector',
        ).distinct()

        if is_sector:
            indicators = indicators.exclude(calculated_indicator=True)
        return indicators
    except Exception as ex:
        # print(ex)
        return indicators


@register.assignment_tag
def get_sub_master_indicators_data(ai_id, is_sector=False):
    from internos.activityinfo.models import Indicator
    indicators = {}
    try:
        indicators = Indicator.objects.filter(sub_indicators=ai_id, master_indicator_sub=True).values(
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
            'target_sector',
            'status_color',
            'status_color_sector',
            'status',
            'status_sector',
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
            'values_tags',
            'cumulative_values_sector',
            'values_partners_sites_sector',
            'values_partners_sector',
            'values_sites_sector',
            'values_sector',
        ).distinct()

        if is_sector:
            indicators = indicators.exclude(calculated_indicator=True)
        return indicators
    except Exception as ex:
        # print(ex)
        return indicators


@register.assignment_tag
def get_indicator_value(indicator, month=None, partner=None, gov=None):
    try:
        value = 0
        if partner and gov and not gov == '0':
            if type(partner) == unicode:
                key = "{}-{}-{}".format(month, gov, partner)
                value += indicator['values_partners_gov'][key]
                return get_indicator_unit(indicator, value)
            if type(gov) == unicode:
                for par in partner:
                    key = "{}-{}-{}".format(month, gov, par)
                    value += indicator['values_partners_gov'][key]
                return get_indicator_unit(indicator, value)
            else:
                for par in partner:
                    for g in gov:
                        key = "{}-{}-{}".format(month, g, par)
                        value += indicator['values_partners_gov'][key]
                return get_indicator_unit(indicator, value)
        if partner:
            if type(partner) == unicode:
                key = "{}-{}".format(month, partner)
                value += indicator['values_partners'][key]
                return get_indicator_unit(indicator, value)
            for par in partner:
                key = "{}-{}".format(month, par)
                value += indicator['values_partners'][key]
            return get_indicator_unit(indicator, value)
        if gov:
            if type(gov) == unicode:
                key = "{}-{}".format(month, gov)
                value += indicator['values_gov'][key]
                return get_indicator_unit(indicator, value)
            for gv in gov:
                key = "{}-{}".format(month, gv)
                if key in indicator['values_gov']:
                    value += indicator['values_gov'][key]
            return get_indicator_unit(indicator, value)
        if gov and not gov == '0':
            key = "{}-{}".format(month, gov)
            return get_indicator_unit(indicator, indicator['values_gov'][key])

        return get_indicator_unit(indicator, indicator['values'][str(month)])
    except Exception as ex:
        # print(ex)
        return get_indicator_unit(indicator, 0)


@register.assignment_tag
def get_indicators_value(indicators, month=None, partner=None, gov=None):
    try:
        value = 0
        for indicator in indicators:
            if partner and gov and not gov == '0':
                if type(partner) == unicode:
                    key = "{}-{}-{}".format(month, gov, partner)
                    value += indicator['values_partners_gov'][key]

                if type(gov) == unicode:
                    for par in partner:
                        key = "{}-{}-{}".format(month, gov, par)
                        value += indicator['values_partners_gov'][key]

                else:
                    for par in partner:
                        for g in gov:
                            key = "{}-{}-{}".format(month, g, par)
                            value += indicator['values_partners_gov'][key]

            if partner:
                if type(partner) == unicode:
                    key = "{}-{}".format(month, partner)
                    value += indicator['values_partners'][key]

                for par in partner:
                    key = "{}-{}".format(month, par)
                    value += indicator['values_partners'][key]

            if gov:
                if type(gov) == unicode:
                    key = "{}-{}".format(month, gov)
                    value += indicator['values_gov'][key]

                for gv in gov:
                    key = "{}-{}".format(month, gv)
                    if key in indicator['values_gov']:
                        value += indicator['values_gov'][key]

            if gov and not gov == '0':
                key = "{}-{}".format(month, gov)
                value += indicator, indicator['values_gov'][key]
            else:
                value += indicator['values'][str(month)]

        return check_indicators_unit(indicators, value)
    except Exception as ex:
        # print(ex)
        return check_indicators_unit(indicators, 0)


@register.assignment_tag
def get_indicator_value_sector(indicator, month=None, partner=None, site=None):
    try:

        value = 0
        if partner and site and not site == '0':
            if type(partner) == unicode:
                key = "{}-{}-{}".format(month, site, partner)
                value += indicator['values_partners_sites_sector'][key]
                return get_indicator_unit(indicator, value)
            for par in partner:
                # key = "{}-{}-{}".format(month, par, gov)
                key = "{}-{}-{}".format(month, site, par)
                value += indicator['values_partners_sites'][key]
            return get_indicator_unit(indicator, value)
        if partner:
            if type(partner) == unicode:
                key = "{}-{}".format(month, partner)
                value += indicator['values_partners_sector'][key]
                return get_indicator_unit(indicator, value)
            for par in partner:
                key = "{}-{}".format(month, par)
                value += indicator['values_partners_sector'][key]
            return get_indicator_unit(indicator, value)
        if site and not site == '0':
            key = "{}-{}".format(month, site)
            return get_indicator_unit(indicator, indicator['values_sites_sector'][key])

        return get_indicator_unit(indicator, indicator['values_sector'][str(month)])
    except Exception as ex:
        # print(ex)
        return get_indicator_unit(indicator, 0)


@register.assignment_tag
def get_indicator_tag_value(indicator, tag):
    try:
        value = 0
        values_tags = indicator['values_tags']
        if tag in values_tags:
            value = values_tags[tag]
        return str(round(value)).replace('.0', '')
    except Exception as ex:
        print(ex)
        return 0


@register.assignment_tag
def get_indicator_live_value(indicator, month=None, partner=None, gov=None):
    try:
        value = 0
        if partner and gov and not gov == '0':
            if type(partner) == unicode:
                key = "{}-{}-{}".format(month, gov, partner)
                value += indicator['values_partners_gov_live'][key]
                return get_indicator_unit(indicator, value)
            if type(gov) == unicode:
                for par in partner:
                    key = "{}-{}-{}".format(month, gov, par)
                    value += indicator['values_partners_gov_live'][key]
                return get_indicator_unit(indicator, value)
            else:
                for par in partner:
                    for g in gov:
                        key = "{}-{}-{}".format(month, g, par)
                        value += indicator['values_partners_gov_live'][key]
                return get_indicator_unit(indicator, value)
        if partner:
            if type(partner) == unicode:
                key = "{}-{}".format(month, partner)
                value += indicator['values_partners_live'][key]
                return get_indicator_unit(indicator, value)
            for par in partner:
                key = "{}-{}".format(month, par)
                value += indicator['values_partners_live'][key]
            return get_indicator_unit(indicator, value)
        if gov:
            if type(gov) == unicode:
                key = "{}-{}".format(month, gov)
                value += indicator['values_gov_live'][key]
                return get_indicator_unit(indicator, value)
            for gv in gov:
                key = "{}-{}".format(month, gv)
                if key in indicator['values_gov_live']:
                    value += indicator['values_gov_live'][key]
            return get_indicator_unit(indicator, value)
        if gov and not gov == '0':
            key = "{}-{}".format(month, gov)
            return get_indicator_unit(indicator, indicator['values_gov_live'][key])

        return get_indicator_unit(indicator, indicator['values_live'][str(month)])
    except Exception as ex:
        return get_indicator_unit(indicator, 0)


@register.assignment_tag
def get_indicator_highest_value(indicator):
    value = 0
    if indicator:
        all_values = indicator['values'].values()
        if all_values:
            max_value = max(all_values)
            return get_indicator_unit(indicator, max_value)

    return value



@register.assignment_tag
def get_array_value(data, key1=None, key2=None, key3=None):
    try:
        # key = '0'

        # if key1:
        #     key = str(key1)

        # if key3:
        #     key = str(key3)

        # if key2 and key3:
        #     key = '{}-{}'.format(key2, key3)

        # if key1 and key2 and key3:
        key = '{}-{}-{}'.format(key1, key2, key3)

        if key in data:
            return data[key]

        return 0
    except Exception as ex:
        # print(ex)
        return 0


@register.assignment_tag
def get_trip_values(data, partner=None, offices=None, section=None):
    result = 0

    if not type(section) == int:
        try:
            for sect in section:
                key = '{}-{}-{}'.format(partner, offices, sect.id)

                if key in data:
                    if type(data[key]) == list:
                        result += len(data[key])
                    else:
                        result += data[key]

            return result
        except Exception as ex:
            # print(ex)
            return 0

    try:
        offices = offices.split(',')

        for office in offices:
            key = '{}-{}-{}'.format(partner, office, section)

            if key in data:
                if type(data[key]) == list:
                    result += len(data[key])
                else:
                    result += data[key]

        return result
    except Exception as ex:
        # print(ex)
        return 0


@register.assignment_tag
def get_databases(is_sector=False):
    from internos.activityinfo.models import Database
    try:
        databases = Database.objects.filter(reporting_year__current=True).exclude(ai_id=10240).order_by('label')
        if is_sector:
            databases = databases.filter(is_sector=True)
        return databases
    except Exception as ex:
        # print(ex)
        return []
