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


@register.assignment_tag
def get_indicator_value(indicator, month=None, partner=None, gov=None):
    # if not month:
    #     return indicator.cumulative_results
    try:
        if partner:
            key = "{}-{}".format(month, partner)
            return indicator.values_partners[key]
        if gov:
            key = "{}-{}".format(month, gov)
            return indicator.values_gov[key]

        return indicator.values.get(str(month))
    except Exception as ex:
        print(ex)
        return 0


# @register.assignment_tag
# def indicator_value(indicator_id, level=0, month=None, partner=None, gov=None):
#     from internos.activityinfo.models import ActivityReport, Indicator
#
#     if level == 0:
#         reports = ActivityReport.objects.filter(indicator_id=indicator_id)
#     if level == 1:
#         indicators = indicator_id.sub_indicators.values_list('id', flat=True).distinct()
#         reports = ActivityReport.objects.filter(ai_indicator_id__in=indicators)
#     if level == 2:
#         reports = reports.sub_indicators.exclude(master_indicator_sub=False, master_indicator=False)
#     if month:
#         reports = reports.filter(start_date__month=month)
#     if partner:
#         reports = reports.filter(partner_id=partner)
#     if gov:
#         reports = reports.filter(location_adminlevel_governorate_code=gov)
#
#     total = reports.aggregate(Sum('indicator_value'))
#     return total['indicator_value__sum'] if total['indicator_value__sum'] else 0
