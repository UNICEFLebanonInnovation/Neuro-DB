import calendar
import json
import datetime
from django import template
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import Group
from django.db.models import Sum
from datetime import date
from internos.activityinfo.models import Indicator
import logging

register = template.Library()
logger = logging.getLogger(__name__)

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
    total = total.replace(",", "")

    if number and total:
        return round((number * 100.0) / total, 2)
    return 0


@register.filter(name='percentage_int')
def percentage_int(number, total):
    total = total.replace(",", "")
    if number:
        return int(round((number * 100.0) / total, 2))
    return 0


@register.filter(name='percentage_float')
def percentage_float(number, total):
    try:
        total = total.replace(",", "")
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
        return '{} {}'.format (int(round(value, 1)), '%')

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
def get_indicator_cumulative_months(indicator, month=None, partner=None, gov=None,start_month=None):
    # try:

    if start_month:
        month_list =[]
        for i in range(start_month,13):
            month_list.append(i)
    value = 0
    cumulative_values = indicator['cumulative_values']
    if partner and gov and month:
        for par in partner:
            for g in gov:
                for m in month:
                    if start_month:
                        if m in start_month:
                            key = "{}-{}-{}".format(m, g, par)
                            if key in indicator['values_partners_gov']:
                                value += indicator['values_partners_gov'][key]
                        else:
                            continue
                    else:
                        key = "{}-{}-{}".format(m, g, par)
                        if key in indicator['values_partners_gov']:
                            value += indicator['values_partners_gov'][key]
        return get_indicator_unit(indicator, value)

    if partner and gov and not month:
        if start_month:
            for par in partner:
                for g in gov:
                    for m in month_list:
                         key = "{}-{}-{}".format(m, g, par)
                         if key in indicator['values_partners_gov']:
                            value += indicator['values_partners_gov'][key]
        else:
            values = cumulative_values.get('partners_govs')
            for par in partner:
                for g in gov:
                    key = "{}-{}".format(g, par)
                    if key in values:
                        value += values[key]
        return get_indicator_unit(indicator, value)

    if partner and month and not gov:
        if type(partner) == unicode:
            for m in month:
                if start_month:
                    if m in month_list:
                        key = "{}-{}".format(m, partner)
                        if key in indicator['values_partners']:
                            value += indicator['values_partners'][key]
                else:
                    key = "{}-{}".format(m, partner)
                    if key in indicator['values_partners']:
                        value += indicator['values_partners'][key]
            return get_indicator_unit(indicator, value)
        else:
            for par in partner:
                for m in month:
                    if start_month:
                        if m in month_list:
                            key = "{}-{}".format(m, par)
                            if key in indicator['values_partners']:
                                value += indicator['values_partners'][key]
                        else:
                            continue
                    else:
                        key = "{}-{}".format(m, par)
                        if key in indicator['values_partners']:
                            value += indicator['values_partners'][key]
            return get_indicator_unit(indicator, value)

    if gov and month and not partner:
            if type(gov) == unicode:
                for m in month:
                    if start_month:
                        if m in month_list:
                            key = "{}-{}".format(m, gov)
                            if key in indicator['values_gov']:
                                value += indicator['values_gov'][key]
                    else:
                        key = "{}-{}".format(m, gov)
                        if key in indicator['values_gov']:
                            value += indicator['values_gov'][key]
                return get_indicator_unit(indicator, value)
            else:
                for g in gov:
                    for m in month:
                        if start_month:
                            if m in month_list:
                                key = "{}-{}".format(m, g)
                                if key in indicator['values_gov']:
                                    value += indicator['values_gov'][key]
                            else:
                                continue
                        else:
                            key = "{}-{}".format(m, g)
                            if key in indicator['values_gov']:
                                 value += indicator['values_gov'][key]
                return get_indicator_unit(indicator, value)

    if partner and 'partners' in cumulative_values:
        if start_month:
            for par in partner:
                for m in month_list:
                     key = "{}-{}".format(m, par)
                     if key in indicator['values_partners']:
                            value += indicator['values_partners'][key]
        else:
            values = cumulative_values.get('partners')
            for par in partner:
                if par in values:
                    value += values[par]
        return get_indicator_unit(indicator, value)

    if gov and 'govs' in cumulative_values:
        if start_month:
            for gv in gov:
                for m in month_list:
                     key = "{}-{}".format(m, gv)
                     if key in indicator['values_gov']:
                            value += indicator['values_gov'][key]
        else:
            values = cumulative_values.get('govs')
            for gv in gov:
                if gv in values:
                    value += values[gv]
        return get_indicator_unit(indicator, value)

    if month and indicator['values']:
        for i in month:
            if start_month:
                if i in month_list:
                    if str(i) in indicator['values']:
                        value = value + float(indicator['values'][str(i)])
                else:
                    continue
            else:
                if str(i) in indicator['values']:
                    value = value + float(indicator['values'][str(i)])
        return get_indicator_unit(indicator, value)

    if start_month:
        if i in month_list:
            if indicator['values']:
                if str(i) in indicator['values']:
                    value = value + float(indicator['values'][str(i)])
                    return get_indicator_unit(indicator, value)
    else:
        if cumulative_values and 'months' in cumulative_values:
            return get_indicator_unit(indicator, cumulative_values.get('months'))

    return get_indicator_unit(indicator, 0)

    # except Exception as ex:
    #     logger.error('get_indicator_cumulative_months error ' + ex.message)
    #     return get_indicator_unit(indicator, 0)


@register.assignment_tag
def get_indicator_cumulative_months_sections(indicator, month=None, partner=None, gov=None,section=None):
    try:
        value = 0
        cumulative_values = indicator['values_cumulative_weekly']

        if partner and gov and month and section:
            for sec in section:
                for par in partner:
                    for g in gov:
                        for m in month:
                            key = "{}-{}-{}-{}".format(m, sec,par,g)
                            if key in indicator['values_sections_partners_gov']:
                                value += indicator['values_sections_partners_gov'][key]
            return get_indicator_unit(indicator, value)

        if partner and gov and section and not month:
            values = cumulative_values.get('sections_partners_gov')
            for sec in section:
                for par in partner:
                    for g in gov:
                        key = "{}-{}-{}".format(sec,par,g)
                        if key in values:
                            value += values[key]
            return get_indicator_unit(indicator, value)

        if partner and month and section and not gov:
            for sec in section:
                for par in partner:
                    for m in month:
                        key = "{}-{}-{}".format(m, sec, par)
                        if key in indicator['values_sections_partners']:
                            value += indicator['values_sections_partners'][key]
            return get_indicator_unit(indicator, value)

        if partner and gov and month and not section :
            for par in partner:
                for g in gov:
                    for m in month :
                        key = "{}-{}-{}".format(m, g, par)
                        if key in indicator['values_partners_gov']:
                          value += indicator['values_partners_gov'][key]
            return get_indicator_unit(indicator, value)

        if partner and gov and not section and not month:
            values = cumulative_values.get('partners_govs')
            for par in partner:
                for g in gov:
                    key = "{}-{}".format(g, par)
                    if key in values:
                        value += values[key]
            return get_indicator_unit(indicator, value)

        if gov and month and section and not partner:
            for sec in section:
                for g in gov:
                    for m in month:
                        key = "{}-{}-{}".format(m, sec, g)
                        if key in indicator['values_sections_gov']:
                            value += indicator['values_sections_gov'][key]
            return get_indicator_unit(indicator, value)

        if partner and section and not month and not gov:
            values = cumulative_values.get('sections_partners')
            for sec in section:
                for par in partner:
                    key = "{}-{}".format(sec, par)
                    if key in values:
                        value += values[key]
            return get_indicator_unit(indicator, value)

        if gov and section and not month and not partner:
            values = cumulative_values.get('sections_gov')
            for sec in section:
                for g in gov:
                    key = "{}-{}".format(sec, g)
                    if key in values:
                        value += values[key]
            return get_indicator_unit(indicator, value)

        if section and month and not gov and not partner:
            if type(section) == unicode:
                for m in month:
                    key = "{}-{}".format(m, section)
                    if key in indicator['values_sections']:
                        value += indicator['values_sections'][key]
                return get_indicator_unit(indicator, value)
            else:
                for sec in section:
                    for m in month:
                        key = "{}-{}".format(m, sec)
                        if key in indicator['values_sections']:
                             value += indicator['values_sections'][key]
                return get_indicator_unit(indicator, value)

        if partner and month and not gov and not section:
            if type(partner) == unicode:
                for m in month:
                    key = "{}-{}".format(m, partner)
                    if key in indicator['values_partners_weekly']:
                        value += indicator['values_partners_weekly'][key]
                return get_indicator_unit(indicator, value)
            else:
                for par in partner:
                    for m in month:
                        key = "{}-{}".format(m, par)
                        if key in indicator['values_partners_weekly']:
                             value += indicator['values_partners_weekly'][key]
                return get_indicator_unit(indicator, value)

        if gov and month and not partner and not section:
            if type(gov) == unicode:
                for m in month:
                    key = "{}-{}".format(m, gov)
                    if key in indicator['values_gov_weekly']:
                         value += indicator['values_gov_weekly'][key]
                return get_indicator_unit(indicator, value)
            else:
                for g in gov:
                    for m in month:
                        key = "{}-{}".format(m, g)
                        if key in indicator['values_gov_weekly']:
                             value += indicator['values_gov_weekly'][key]
                return get_indicator_unit(indicator, value)

        if partner and gov and not month and not section:
            values = cumulative_values.get('partners_govs')
            for par in partner:
                for g in gov:
                    key = "{}-{}".format(g, par)
                    if key in values:
                        value += values[key]
            return get_indicator_unit(indicator, value)

        if partner and 'partners' in cumulative_values:
            values = cumulative_values.get('partners')
            for par in partner:
                if par in values:
                    value += values[par]
            return get_indicator_unit(indicator, value)

        if gov and 'govs' in cumulative_values:
            values = cumulative_values.get('govs')
            for gv in gov:
                if gv in values:
                    value += values[gv]
            return get_indicator_unit(indicator, value)

        if section and 'sections' in cumulative_values:
            values = cumulative_values.get('sections')
            for sec in section:
                if sec in values:
                    value += values[sec]
            return get_indicator_unit(indicator, value)

        if month and indicator['values_weekly']:
            for i in month:
                if str(i) in indicator['values_weekly']:
                    value = value + float(indicator['values_weekly'][str(i)])
            return get_indicator_unit(indicator, value)

        if cumulative_values and 'months' in cumulative_values:
            value = cumulative_values.get('months')
            return get_indicator_unit(indicator,value)

        return get_indicator_unit(indicator, 0)

    except Exception as ex:
        logger.error('get_indicator_cumulative_months_sections ' + ex.message)
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
        logger.error('get_indicator_partner_cumulative error ' + ex.message)
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
        logger.error('get_indicators_partner_cumulative error ' + ex.message)
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
        logger.error('get_indicator_cumulative_sector error  ' + ex.message)
        return get_indicator_unit(indicator, 0)


@register.assignment_tag
def get_indicator_live_cumulative(indicator, month=None, partner=None, gov=None):
    try:
        value= 0
        cumulative_values = indicator['cumulative_values_live']
        if partner and gov :
            cumulative_values = cumulative_values.get('partners_govs')
            for par in partner:
                for g in gov:
                    key = "{}-{}".format(g, par)
                    if key in cumulative_values:
                        value += cumulative_values[key]
            return get_indicator_unit(indicator, value)

        if partner and not gov and 'partners' in cumulative_values:
            cumulative_values = cumulative_values.get('partners')
            for par in partner:
                if par in cumulative_values:
                    value += cumulative_values[par]
            return get_indicator_unit(indicator, value)

        if gov and not partner and 'govs' in cumulative_values:
            cumulative_values = cumulative_values.get('govs')
            for gv in gov :
                if gv in cumulative_values:
                    value += cumulative_values[gv]
            return get_indicator_unit(indicator, value)

        if 'months' in cumulative_values:
            return get_indicator_unit(indicator, cumulative_values.get('months'))

        # if month and 'months' in cumulative_values:
        #     month = str(month)
        #     cumulative_values = cumulative_values.get('months')
        #     if month in cumulative_values:
        #         return get_indicator_unit(indicator, cumulative_values[month])

        return get_indicator_unit(indicator, 0)
    except Exception as ex:
        logger.error('get_indicator_live_cumulative error'  + ex.message)
        return get_indicator_unit(indicator, 0)

@register.assignment_tag
def get_indicator_live_cumulative_section(indicator, month=None, partner=None, gov=None,section=None):
    try:
        value = 0
        cumulative_values = indicator['cumulative_values_live']
        if partner and gov and section:
            cumulative_values = cumulative_values.get('sections_partners_gov')
            for sec in section:
                for par in partner:
                    for g in gov:
                        key = "{}-{}-{}".format(sec,par,g)
                        if key in cumulative_values:
                            value += cumulative_values[key]
            return get_indicator_unit(indicator, value)

        if partner and gov and not section:
            cumulative_values = cumulative_values.get('partners_govs')
            for par in partner:
                for g in gov:
                    key = "{}-{}".format(g, par)
                    if key in cumulative_values:
                        value += cumulative_values[key]
            return get_indicator_unit(indicator, value)

        if partner and section and not gov:
            cumulative_values = cumulative_values.get('sections_partners')
            for sec in section:
                for par in partner:
                    key = "{}-{}".format(sec, par)
                    if key in cumulative_values:
                        value += cumulative_values[key]
            return get_indicator_unit(indicator, value)

        if section and gov and not partner:
            cumulative_values = cumulative_values.get('sections_gov')
            for sec in section:
                for gv in gov:
                    key = "{}-{}".format(sec, gv)
                    if key in cumulative_values:
                        value += cumulative_values[key]
            return get_indicator_unit(indicator, value)

        if partner and not gov and not section and 'partners' in cumulative_values:
            cumulative_values = cumulative_values.get('partners')
            for par in partner:
                if par in cumulative_values:
                    value += cumulative_values[par]
            return get_indicator_unit(indicator, value)

        if gov and not partner and not section and 'govs' in cumulative_values:
            cumulative_values = cumulative_values.get('govs')
            for gv in gov :
                if gv in cumulative_values:
                    value += cumulative_values[gv]
            return get_indicator_unit(indicator, value)

        if section and not partner and not gov and 'sections' in cumulative_values:
            cumulative_values = cumulative_values.get('sections')
            for sec in section :
                if sec in cumulative_values:
                    value += cumulative_values[sec]
            return get_indicator_unit(indicator, value)

        if 'months' in cumulative_values:
            return get_indicator_unit(indicator, cumulative_values.get('months'))

        # if month and 'months' in cumulative_values:
        #     month = str(month)
        #     cumulative_values = cumulative_values.get('months')
        #     if month in cumulative_values:
        #         return get_indicator_unit(indicator, cumulative_values[month])

        return get_indicator_unit(indicator, 0)
    except Exception as ex:
        logger.error('get_indicator_live_cumulative_section error' + ex.message)
        return get_indicator_unit(indicator, 0)


@register.assignment_tag
def calculate_achievement_new(target, cumulative_values):
    achieved = 0
    if int(target) == 0:
        return 0
    try:
        value = cumulative_values.replace(",","")
        achieved = round((int(value )* 100.0) / target, 2)
    except Exception:
        return achieved
    return achieved


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
        logger.error('calculate_achievement error' + ex.message)
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
        logger.error('get_indicator_live_achieved error' + ex.message)
        return 0


@register.assignment_tag
def get_indicator_hpm_data(ai_id, month=None):

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

        # last_month_number = 12

        cumulative = 0
        if str(month) == str(last_month_number):
            cumulative_values = indicator.cumulative_values
        else:
            cumulative_values = indicator.cumulative_values_hpm

        values_hpm = indicator.values_hpm
        previous_month = int(month) - 1
        last_month_value = 0

        if 'months' in indicator.cumulative_values_hpm:
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
        logger.error('get_indicator_hpm_data error' + ex.message)
        return data


@register.assignment_tag
def get_hpm_indicators(db_id):
    from internos.activityinfo.models import Indicator, Database
    db_indicators = {}
    db = Database.objects.get(ai_id=int(db_id))
    indicators = Indicator.objects.filter(activity__database=db, hpm_indicator=True, master_indicator=True).order_by(
        'sequence')
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
        'values_tags',
        'cumulative_values_sector',
        'comment',
        'hpm_label',
        'has_hpm_note',
        'target_hpm',
        'hpm_additional_cumulative',
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
def get_hpm_indicator_data_new(indicator_id, month=None):
    data = {
        'id': 0,
        'name': 0,
        'hpm_label': 0,
        'cumulative': 0,
        'target': 0,
        'target_sector': 0,
        'report_change': 0,
        'sector_cumulative': 0,
        'sector_change': 0,
        'comment': "",
        'has_hpm_note': 0,
        'highest': 0,
        'highest_change': 0,
        'is_cumulative': 0,
        'boys': 0,
        'girls': 0,
        'male': 0,
        'female': 0,
    }
    try:
        value = 0
        sector_value = 0
        cumulative = 0
        cumulative_sector = 0
        max_value = 0
        max_value_pre = 0
        current_month = date.today().month

        if month is None:
            month = current_month

        try:
            indicator = Indicator.objects.get(id=int(indicator_id))
        except Exception as ex:
            return data

        if indicator.is_cumulative == False:
            all_values = indicator.values
            if all_values:
                max_value = all_values['1']
                max_value_pre = all_values['1']
                for key in all_values.keys():
                    if key <= str(month):
                        item_value = all_values[key]
                        if item_value > max_value:
                            max_value = item_value

                    if key <= str(month - 1):
                        item_value_pre = all_values[key]
                        if item_value_pre > max_value_pre:
                            max_value_pre = item_value_pre

        additional_cumulative = indicator.hpm_additional_cumulative
        # get additional cumulative for indicators of PPL that starts last year at month 8 to be added to current year

        if int(month) == current_month:
                 if indicator.cumulative_values:
                     if 'months' in indicator.cumulative_values:
                       if indicator.cumulative_values['months']:
                        value = indicator.cumulative_values['months']


                 if indicator.cumulative_values_sector:
                    if 'months' in indicator.cumulative_values_sector:
                        if indicator.cumulative_values_sector['months']:
                         sector_value = indicator.cumulative_values_sector['months']

        else:
            for m in range(1, month + 1):
                if indicator.values:
                    if str(m) in indicator.values:
                        value += float(indicator.values[str(m)])


                if indicator.values_sector:
                    if str(m) in indicator.values_sector:
                        sector_value += float(indicator.values_sector[str(m)])

        previous_sector_values = 0
        for m in range(1, month):
            if indicator.values_sector:
                if str(m) in indicator.values_sector:
                    previous_sector_values += indicator.values_sector[str(m)]

        previous_values = 0
        for m in range(1, month):
            if indicator.values:
                if str(m) in indicator.values:
                    previous_values += indicator.values[str(m)]

        value = value + additional_cumulative
        previous_values = previous_values+additional_cumulative

        if int(month) == 1:
            report_change = 0
            sector_change = 0
            highest_change = 0
        else:

            report_change = "{:,}".format(round((value - previous_values), 1))
            report_change = report_change.replace('.0', '')

            highest_change = "{:,}".format(round((max_value - max_value_pre), 1))
            highest_change = highest_change.replace('.0', '')

            sector_change = "{:,}".format(round((sector_value - previous_sector_values), 1))
            sector_change = sector_change.replace('.0', '')

        cumulative = "{:,}".format(round(value), 1)
        cumulative = cumulative.replace('.0', '')




        max_value = "{:,}".format(round(max_value), 1)
        max_value = max_value.replace('.0', '')

        sector_cumulative = "{:,}".format(round(sector_value), 1)
        sector_cumulative = sector_cumulative.replace('.0', '')

        target = 0
        if indicator.target_hpm == 0:
            target = indicator.target
        else:
            target = indicator.target_hpm
        comment = ""

        if indicator.comment is not None:
             if str(month) in indicator.comment:
                comment = indicator.comment[str(month)]
        data = {
            'id': indicator.id,
            'name': indicator.name,
            'target': "{:,}".format(target),
            'target_sector': "{:,}".format(indicator.target_sector),
            'cumulative': cumulative,
            'sector_cumulative': sector_cumulative,
            'report_change': report_change,
            'sector_change': sector_change,
            'comment': comment,
            'has_hpm_note': indicator.has_hpm_note,
            'hpm_label': indicator.hpm_label,
            'highest': max_value,
            'highest_change': highest_change,
            'is_cumulative': indicator.is_cumulative,
            'boys': str(round(indicator.values_tags['boys'])).replace('.0',
                                                                         '') if 'boys' in indicator.values_tags else 0,
            'girls': str(round(indicator.values_tags['girls'])).replace('.0',
                                                                           '') if 'girls' in indicator.values_tags else 0,
            'male': str(round(indicator.values_tags['male'])).replace('.0',
                                                                         '') if 'male' in indicator.values_tags else 0,
            'female': str(round(indicator.values_tags['female'])).replace('.0',
                                                                             '') if 'female' in indicator.values_tags else 0, }

        return data
    except Exception as ex:
        return data


# function to get sub-indicators added from admin used in education database
@register.assignment_tag
def get_hpm_sub_indicators(indicator_id):
    from internos.activityinfo.models import Indicator
    list = []
    indicator = Indicator.objects.get(id=indicator_id)
    if indicator:
        list = Indicator.objects.filter(hpm_indicator=True, master_indicator=False,
                                        activity=indicator.activity).order_by('sequence').values(
            'id',
            'ai_id',
            'name',
            'hpm_label',
            'measurement_type',
            'units',
            'target',
            'target_hpm',
            'target_sector',
            'cumulative_values',
            'values',
            'comment',
            'has_hpm_note',
            'values_tags',
            'cumulative_values_sector',
            'values_sector',
        ).distinct()
    return list


@register.assignment_tag
def get_sub_indicators_data(ai_id, is_sector=False, ai_db=None):
    from internos.activityinfo.models import Indicator
    indicators = {}
    try:
        if ai_db:
            indicators = Indicator.objects.filter(sub_indicators=ai_id,activity__database =ai_db)
        else:
            # cursor = connection.cursor()
            # cursor.execute("SELECT DISTINCT ON (activityinfo_indicator.id) activityinfo_indicator.id, activityinfo_indicator.ai_id, activityinfo_indicator.name, activityinfo_indicator.master_indicator, activityinfo_indicator.master_indicator_sub, activityinfo_indicator.master_indicator_sub_sub, activityinfo_indicator.individual_indicator, activityinfo_indicator.explication, activityinfo_indicator.awp_code, activityinfo_indicator.measurement_type, activityinfo_indicator.units, activityinfo_indicator.target, activityinfo_indicator.target_sector, activityinfo_indicator.status_color, activityinfo_indicator.status_color_sector, activityinfo_indicator.status, activityinfo_indicator.status_sector, activityinfo_indicator.cumulative_values, activityinfo_indicator.values_partners_gov, activityinfo_indicator.values_partners, activityinfo_indicator.values_gov, activityinfo_indicator.values, activityinfo_indicator.values_live, activityinfo_indicator.values_gov_live, activityinfo_indicator.values_partners_live, activityinfo_indicator.values_partners_gov_live, activityinfo_indicator.cumulative_values_live, activityinfo_indicator.values_tags, activityinfo_indicator.cumulative_values_sector, activityinfo_indicator.values_partners_sites_sector, activityinfo_indicator.values_partners_sector, activityinfo_indicator.values_sites_sector, activityinfo_indicator.values_sector, activityinfo_indicator.is_cumulative, activityinfo_indicator.category, activityinfo_indicator.values_sections, activityinfo_indicator.values_sections_partners, activityinfo_indicator.values_sections_gov, activityinfo_indicator.values_sections_partners_gov, activityinfo_indicator.values_weekly, activityinfo_indicator.values_gov_weekly, activityinfo_indicator.values_partners_weekly, activityinfo_indicator.values_partners_gov_weekly, activityinfo_indicator.values_cumulative_weekly, activityinfo_indicator.activity_id FROM activityinfo_indicator INNER JOIN activityinfo_indicator_sub_indicators ON (activityinfo_indicator.id = activityinfo_indicator_sub_indicators.from_indicator_id) WHERE activityinfo_indicator_sub_indicators.to_indicator_id = "+str(ai_id)+" ORDER BY activityinfo_indicator.id ASC")
            # rows = cursor.fetchall()
            # print(json.dumps(rows))

            indicators = Indicator.objects.filter(sub_indicators=ai_id)
        indicators=indicators.values(
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
            'is_cumulative',
            'category',
            'values_sections',
            'values_sections_partners',
            'values_sections_gov',
            'values_sections_partners_gov',
            'values_weekly',
            'values_gov_weekly',
            'values_partners_weekly',
            'values_partners_gov_weekly',
            'values_cumulative_weekly',
            'activity'
        ).order_by('id').distinct('id')

        if is_sector:
            indicators = indicators.exclude(calculated_indicator=True)
        return indicators
    except Exception as ex:
        print(ex.message)
        logger.error('get_sub_indicators_data error' + ex.message)
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
        logger.error('get_sub_master_indicators_data error' + ex.message)
        return indicators


@register.assignment_tag
def get_indicator_value(indicator, month=None, partner=None, gov=None):

    try:
        if partner and type(partner) == unicode:
            partner = [partner]

        if gov and type(gov) == unicode:
            gov = [gov]

        value = 0
        if partner and gov:
            for par in partner:
                for g in gov:
                    key = "{}-{}-{}".format(month, g, par)
                    if key in indicator['values_partners_gov']:
                        value += indicator['values_partners_gov'][key]
            return get_indicator_unit(indicator, value)

        if partner and not gov:
            for par in partner:
                key = "{}-{}".format(month, par)
                if key in indicator['values_partners']:
                    value += indicator['values_partners'][key]
            return get_indicator_unit(indicator, value)

        if gov and not partner:
            for gv in gov:
                key = "{}-{}".format(month, gv)
                if key in indicator['values_gov']:
                    value += indicator['values_gov'][key]
            return get_indicator_unit(indicator, value)

        if not gov and not partner:
             if str(month) in indicator['values']:
                return get_indicator_unit(indicator, indicator['values'][str(month)])

        return get_indicator_unit(indicator, 0)
    except Exception as ex:
        logger.error('get_indicator_value error' + ex.message)
        return get_indicator_unit(indicator, 0)


@register.assignment_tag
def get_indicator_value_section(indicator, month=None, partner=None, gov=None,section=None):
      try:
        value = 0
        if partner and gov and section:
            for sec in section:
                for par in partner:
                    for g in gov:
                        key = "{}-{}-{}-{}".format(month,sec, par,g)
                        if key in indicator['values_sections_partners_gov']:
                            value += indicator['values_sections_partners_gov'][key]
            return get_indicator_unit(indicator, value)

        if partner and gov and not section:
           for par in partner:
               for gv in gov:
                    key = "{}-{}-{}".format(month,gv,par)
                    if key in indicator['values_partners_gov_weekly']:
                        value += indicator['values_partners_gov_weekly'][key]
           return get_indicator_unit(indicator, value)

        if partner and section and not gov:
           for sec in section:
               for par in partner:
                    key = "{}-{}-{}".format(month, sec,par)
                    if key in indicator['values_sections_partners']:
                        value += indicator['values_sections_partners'][key]
           return get_indicator_unit(indicator, value)

        if gov and section and not partner:
            for sec in section:
                for gv in gov:
                    key = "{}-{}-{}".format(month,sec, gv)
                    if key in indicator['values_sections_gov']:
                        value += indicator['values_sections_gov'][key]
            return get_indicator_unit(indicator, value)

        if partner and not gov and not section:
            for par in partner:
                key = "{}-{}".format(month, par)
                if key in indicator['values_partners_weekly']:
                    value += indicator['values_partners_weekly'][key]
            return get_indicator_unit(indicator, value)

        if gov and not partner and not section:
            for gv in gov:
                key = "{}-{}".format(month, gv)
                if key in indicator['values_gov_weekly']:
                    value += indicator['values_gov_weekly'][key]
            return get_indicator_unit(indicator, value)

        if section and not partner and not gov:
            for sec in section:
                key = "{}-{}".format(month, sec)
                if key in indicator['values_sections']:
                    value += indicator['values_sections'][key]
            return get_indicator_unit(indicator, value)

        if not gov and not partner and not section:
             if str(month) in indicator['values_weekly']:
                return get_indicator_unit(indicator, indicator['values_weekly'][str(month)])

        return get_indicator_unit(indicator, 0)
      except Exception as ex:
         logger.error('get_indicator_value_section error' + ex.message)
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
        logger.error('get_indicators_value error' + ex.message)
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
        logger.error('get_indicator_value_sector error' + ex.message)
        return get_indicator_unit(indicator, 0)


@register.assignment_tag
def get_indicator_tag_value(indicator, tag, month=None, partners=None, governorates=None, sections=None):
    # try:
        value = 0
        values_tags = indicator['values_tags']
        if partners and governorates and sections and month:
            for par in partners:
                for gov in governorates:
                    for sec in sections:
                        for m in month:
                            key= '{}--{}--{}--{}-{}'.format(m, sec, par,gov,tag)
                            if 'partners_govs_sections_'+tag in values_tags:
                                if key in values_tags['partners_govs_sections_'+tag]:
                                    value += values_tags['partners_govs_sections_'+tag][key]
                                return str(round(value)).replace('.0', '')

        if partners and governorates and month:
            for par in partners:
                for gov in governorates:
                    for m in month:
                        key = '{}--{}--{}--{}'.format(m, gov, par,tag)
                        if 'partners_govs_'+ tag in values_tags:
                            if key in values_tags['partners_govs_'+ tag]:
                                value += values_tags['partners_govs_'+tag][key]
                            return str(round(value)).replace('.0', '')

        if partners and sections and month:
            for par in partners:
                for sec in sections:
                    for m in month:
                        key = '{}--{}--{}--{}'.format(m, sec, par,tag)
                        if 'partners_sections_'+ tag in values_tags:
                            if key in values_tags['partners_sections_'+ tag]:
                                value += values_tags['partners_sections_'+tag][key]
                            return str(round(value)).replace('.0', '')

        if governorates and sections and month:
            for gv in governorates:
                for sec in sections:
                    for m in month:
                        key = '{}--{}--{}--{}'.format(m, sec, gv,tag)
                        if 'govs_sections_'+ tag in values_tags:
                            if key in values_tags['govs_sections_'+ tag]:
                                value += values_tags['govs_sections_'+tag][key]
                            return str(round(value)).replace('.0', '')

        if partners and governorates and sections:
            for par in partners:
                for gov in governorates:
                    for sec in sections:
                        key = '{}--{}--{}--{}'.format(sec, par, gov,tag)
                        if 'cum_section_par_gov_' + tag in values_tags:
                            if key in values_tags['cum_section_par_gov_' + tag]:
                                value += values_tags['cum_section_par_gov_' + tag][key]
                        return str(round(value)).replace('.0', '')

        if partners and governorates:
            for par in partners:
                for gov in governorates:
                    key = '{}--{}--{}'.format(par,gov,tag)
                    if 'cum_partner_gov_' + tag in values_tags:
                        if key in values_tags['cum_partner_gov_' + tag]:
                            value += values_tags['cum_partner_gov_' + tag][key]
                        return str(round(value)).replace('.0', '')

        if partners and sections:
            for par in partners:
                for sec in sections:
                    key = '{}--{}--{}'.format(sec, par,tag)
                    if 'cum_section_partner_' + tag in values_tags:
                        if key in values_tags['cum_section_partner_' + tag]:
                            value += values_tags['cum_section_partner_' + tag][key]
                        return str(round(value)).replace('.0', '')

        if governorates and sections:
            for gv in governorates:
                for sec in sections:
                    key = '{}--{}--{}'.format(sec, gv,tag)
                    if 'cum_sec_gov_' + tag in values_tags:
                        if key in values_tags['cum_sec_gov_' + tag]:
                            value += values_tags['cum_sec_gov_' + tag][key]
                        return str(round(value)).replace('.0', '')

        if partners:
            for par in partners:
                key = '{}--{}'.format(par,tag)
                if 'cum_partners_' + tag in values_tags:
                    if key in values_tags['cum_partners_' + tag]:
                        value += values_tags['cum_partners_' + tag][key]
                    return str(round(value)).replace('.0', '')
        if governorates:
            for gv in governorates:
                key = '{}--{}'.format(gv,tag)
                if 'cum_govs_' + tag in values_tags:
                    if key in values_tags['cum_govs_' + tag]:
                        value += values_tags['cum_govs_' + tag][key]
                    return str(round(value)).replace('.0', '')

        if sections:
            for sec in sections:
                key = '{}--{}'.format(sec,tag)
                if 'cum_sections_' + tag in values_tags:
                    if key in values_tags['cum_sections_' + tag]:
                        value += values_tags['cum_sections_' + tag][key]
                    return str(round(value)).replace('.0', '')

        if month:
            for m in month:
                key = '{}--{}'.format(m,tag)
                if 'months_'+ tag in values_tags:
                    if key in values_tags['months_' + tag]:
                        value += values_tags['months_' + tag][key]
                    return str(round(value)).replace('.0', '')

        if tag in values_tags:
            value = values_tags[tag]
        return str(round(value)).replace('.0', '')
    # except Exception as ex:
    #     logger.error('get_indicator_tag_value error' + ex.message)
    #     return 0


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
        logger.error('get_indicator_live_value error' + ex.message)
        return get_indicator_unit(indicator, 0)


@register.assignment_tag
def get_indicator_highest_value(indicator):
    value = 0
    try:
        if indicator:
            all_values = indicator['values'].values()
            if all_values:
                max_value = max(all_values)
                return get_indicator_unit(indicator, max_value)
        return value
    except Exception as ex:
        logger.error('get_indicator_highest_value error' + ex.message)
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
        logger.error('get_array_value error' + ex.message)
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
            logger.error('get_trip_values error' + ex.message)
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
        print('get_trip_values 2 error' + ex.message)
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
        print('get_databases error' + ex.message)
        return []


@register.assignment_tag
def increment(counter):
    counter = counter + 1
    return counter


@register.assignment_tag
def get_Crisis_db():
    from internos.activityinfo.models import Database
    try:
        databases = Database.objects.filter(reporting_year__name='2020_Crisis').order_by('label')
        return databases
    except Exception as ex:
        print('get_Crisis_db error' + ex.message)
        return []


@register.assignment_tag
def split_results(key,value):
    d = dict()
    month_num = key.split('-')[0]
    month = calendar.month_name[int(month_num)]
    gov = key.split('-')[1]
    result = value
    governorates = []
    governorates.append((2, 'Akkar'))
    governorates.append((3, ' Baalbek_Hermel'))
    governorates.append((4, 'North'))
    governorates.append((5, 'Mount Lebanon'))
    governorates.append((6, 'Bekaa'))
    governorates.append((7, 'Beirut'))
    governorates.append((8, 'South'))
    governorates.append((9, 'Nabatiye'))
    governorates.append((10, 'National'))

    gov_name = ""
    for num, name in governorates:
        if num == int(gov):
            gov_name = name


    d['month'] = month
    d['month_num'] =month_num
    d['result'] = result
    d['gov'] = gov
    d['gov_name'] = gov_name

    return d


@register.assignment_tag
def get_database_by_activity(activity_id):
    from internos.activityinfo.models import Activity, Database

    database = ""
    try:
        activity = Activity.objects.get(id=activity_id)
        return activity.database
    except Exception as ex:
         print('get_database_by_activity error' + ex.message)
    return database


@register.assignment_tag
def get_tag_name(tag_id):
    from internos.activityinfo.models import IndicatorTag

    tag_name = ""
    try:
        tag = IndicatorTag.objects.get(id=tag_id)
        return tag.label
    except Exception as ex:
        print('get_tag_name error' + ex.message)
    return tag_name


@register.assignment_tag
def get_indicator_reporting_unit(indicator_id):
    from internos.activityinfo.models import ActivityReport
    unit=""
    try:
        report = ActivityReport.objects.filter(ai_indicator=indicator_id).first().values(
            'id',
            'ai_indicator',
            'indicator_units',
        )
        unit = report['indicator_units']
        return unit
    except Exception as ex :
        # print('get_indicator_reporting_unit error' + ex.message)
        return unit



