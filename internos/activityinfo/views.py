from __future__ import absolute_import, unicode_literals

import os
import json
import datetime
import calendar
from django.db.models import Q, Sum
from dal import autocomplete
from django.views.generic import ListView, TemplateView, FormView
from django.http import HttpResponse, JsonResponse
from .models import ActivityReport, LiveActivityReport, Database, Indicator, Partner, IndicatorTag, ReportingYear, Activity
from django.shortcuts import render
from datetime import date
from django.http import HttpResponseRedirect
from .templatetags.util_tags import get_sub_indicators_data, get_sub_indicators_data_new, \
    get_indicator_cumulative_months_sections, get_indicator_cumulative_months, get_sub_indicators_crisis_data, \
    get_sub_indicators_live_crisis_data, get_sub_indicators_live_data, get_indicator_live_cumulative, \
    get_indicator_live_cumulative_section, get_indicator_highest_value, calculate_achievement_new, \
    get_indicator_highest_value_live, get_sub_master_indicators_data, get_sub_master_indicators_crisis_data
from .utils import get_partners_list, get_governorates_list, get_reporting_sections_list, get_cadastrals_list, \
    get_months_list
from .utils import calculate_internal_indicators_values, calculate_internal_cumulative_results


class IndexView(TemplateView):
    template_name = 'activityinfo/index.html'

    def get_context_data(self, **kwargs):
        year = date.today().year
        instance = ReportingYear.objects.get(current=True)
        reporting_year = self.request.GET.get('rep_year', instance.year)
        databases = Database.objects.filter(reporting_year__name=reporting_year,
                                            display=True).exclude(ai_id=10240).order_by('label')
        return {
            'ai_databases': databases,
            'reporting_year': reporting_year
        }


class DashboardView(TemplateView):
    template_name = 'activityinfo/dashboard.html'

    def get_context_data(self, **kwargs):
        month = int(self.request.GET.get('month', int(datetime.now().strftime("%m")) - 1))
        month_name = self.request.GET.get('month', datetime.now().strftime("%B"))
        ai_id = int(self.request.GET.get('ai_id', 0))

        year = date.today().year
        reporting_year = self.request.GET.get('rep_year', year)

        if ai_id:
            database = Database.objects.get(ai_id=ai_id)
        else:
            try:
                section = self.request.user.section
                database = Database.objects.get(section=section, reporting_year__name=reporting_year)
            except Exception:
                database = Database.objects.filter(reporting_year__name=reporting_year).first()

        report = ActivityReport.objects.filter(
            database=database,
            start_date__month=month,
            funded_by__contains='UNICEF')
        months = ActivityReport.objects.values('month_name').distinct()
        partners = report.values('partner_id').distinct().count()
        activity_categories = report.values('form_category').distinct().count()
        activities = report.values('form').distinct().count()
        indicators = report.values('indicator_name').distinct().count()
        unicef_funds = report.filter(funded_by__contains='UNICEF').values('funded_by').count()
        not_reported = report.filter(Q(indicator_value__isnull=True) | Q(indicator_value=0)).count()

        return {
            'month': month,
            'month_name': month_name,
            'months': months,
            'months_nbr': months.count(),
            'database': database,
            'partners': partners,
            'activity_categories': activity_categories,
            'activities': activities,
            'not_reported': not_reported,
            'indicators': indicators,
            'unicef_funds': unicef_funds
        }


class ReportView(TemplateView):
    template_name = 'activityinfo/report.html'

    def get_context_data(self, **kwargs):
        selected_filter = False
        display_live = True
        selected_partners = self.request.GET.getlist('partners', [])
        selected_months = self.request.GET.getlist('months', [])
        selected_governorates = self.request.GET.getlist('governorates', [])
        support_covid = self.request.GET.get('support_covid', -1)

        current_year = date.today().year
        current_month = date.today().month
        partner_info = {}
        today = datetime.date.today()
        first = today.replace(day=1)
        last_month = first - datetime.timedelta(days=1)
        month_number = last_month.strftime("%m")
        month = int(last_month.strftime("%m"))
        month_name = last_month.strftime("%B")

        # month_number = '12'
        # month = 12
        # month_name = 'December'

        ai_id = int(self.request.GET.get('ai_id', 0))

        database = Database.objects.get(ai_id=ai_id)

        reporting_year = database.reporting_year.name
        months = []
        if selected_partners or selected_governorates or selected_months:
            selected_filter = True
            partners = get_partners_list(database, govs=selected_governorates,months=selected_months)
            governorates = get_governorates_list(database,partners=selected_partners,months=selected_months)

            if selected_months is not None and len(selected_months) > 0:
                for mon in selected_months:
                    months.append((mon, calendar.month_name[int(mon)]))
            else:
                months = get_months_list(database, selected_partners, selected_governorates)
        else:
            partners = get_partners_list(database)
            governorates = get_governorates_list(database)
            if int(reporting_year) == current_year:

                for i in range(1, current_month):
                    months.append((i, datetime.date(2008, i, 1).strftime('%B')))
            else:
                for i in range(1, 13):
                    months.append((i, datetime.date(2008, i, 1).strftime('%B')))

        all_indicators = Indicator.objects.filter(activity__database=database).order_by('sequence')

        if int(support_covid) == 1:
            master_indicators = all_indicators.filter(activity__database=database, support_COVID=True).exclude(is_sector=True).order_by('sequence')

        elif int(support_covid) == 0:
            master_indicators = all_indicators.filter(activity__database=database, support_COVID=False).exclude(is_sector=True).order_by( 'sequence')

        else:
            master_indicators = all_indicators.filter(activity__database=database).exclude(is_sector=True).order_by( 'sequence')

        if database.mapped_db:
            master_indicators1 = master_indicators.filter(master_indicator=True)
            master_indicators2 = master_indicators.filter(sub_indicators__isnull=True, individual_indicator=True)
            master_indicators = master_indicators1 | master_indicators2

       # none_ai_indicators = Indicator.objects.filter(activity__none_ai_database=database).exclude(is_sector=True)
        master_indicators = master_indicators.values(
            'id',
            'ai_id',
            'name',
            'master_indicator',
            'master_indicator_sub',
            'individual_indicator',
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
            'is_cumulative',
            'support_COVID',
            'highest_values',

        ).distinct()

        for master_ind in master_indicators:
            if master_ind['is_cumulative']:
                master_ind['cumulative'] = get_indicator_cumulative_months(master_ind, selected_months,
                                                                                selected_partners,
                                                                                selected_governorates,
                                                                                )
            else:
                master_ind['cumulative'] = get_indicator_highest_value(master_ind, selected_months,
                                                                           selected_partners,
                                                                           selected_governorates,
                                                                           )
            master_ind['achieved'] = str(calculate_achievement_new(master_ind['target'], master_ind['cumulative']))+ '%'

            sub_indicators = get_sub_indicators_data_new(master_ind['id'], all_indicators)
            master_ind['sub_list'] = sub_indicators
            master_ind['sub_list_filtered'] = sub_indicators
            for sub_ind in sub_indicators:
                if sub_ind['master_indicator']:
                    sub_ind['cumulative'] = 0
                    continue
                else:
                    if master_ind['is_cumulative']:
                        sub_ind['cumulative'] = get_indicator_cumulative_months(sub_ind,  selected_months,
                                                                                selected_partners,
                                                                                selected_governorates,
                                                                                )
                    else:
                        sub_ind['cumulative'] = get_indicator_highest_value(sub_ind, selected_months,
                                                                                selected_partners,
                                                                                selected_governorates,
                                                                                )
                    if sub_ind['master_indicator_sub']:
                        sub_ind['achieved'] = str(calculate_achievement_new(sub_ind['target'], sub_ind['cumulative']) )+ '%'

                sub_sub_indicators = get_sub_indicators_data_new(sub_ind['id'], all_indicators)
                sub_ind['sub_list'] = sub_sub_indicators
                sub_ind['sub_list_filtered'] = sub_sub_indicators
                for ind in sub_sub_indicators:
                    if ind['master_indicator']:
                        ind['cumulative'] = 0
                        continue
                    else:
                        if master_ind['is_cumulative']:
                            ind['cumulative'] = get_indicator_cumulative_months(ind, selected_months,
                                                                                selected_partners,
                                                                                selected_governorates,
                                                                                )
                        else:
                            ind['cumulative'] = get_indicator_highest_value(ind, selected_months,
                                                                                selected_partners,
                                                                                selected_governorates,
                                                                                )

        filtered_list = []
        if selected_filter:
            for master_ind in master_indicators:
                if not (master_ind['cumulative'] == '0' or master_ind['cumulative'] == 0):
                    filtered_list.append(master_ind)
                    master_ind['sub_list_filtered'] = []
                    for sub_indicator in master_ind['sub_list']:
                        sub_indicator['sub_list_filtered'] = []
                        if not (sub_indicator['cumulative'] == '0' or sub_indicator['cumulative'] == 0):
                            master_ind['sub_list_filtered'].append(sub_indicator)
                        for sub_sub_ind in sub_indicator['sub_list']:
                            if sub_sub_ind['cumulative'] == '0' or sub_sub_ind['cumulative'] == 0:
                                continue
                            else:
                                sub_indicator['sub_list_filtered'].append(sub_sub_ind)
                else:
                    for sub_indicator in master_ind['sub_list']:
                        if not (sub_indicator['cumulative'] == '0' or sub_indicator['cumulative'] == 0):
                            filtered_list.append(sub_indicator)
                            sub_indicator['sub_list_filtered'] = []
                            for sub_sub_ind in sub_indicator['sub_list']:
                                if sub_sub_ind['cumulative'] == '0' or sub_sub_ind['cumulative'] == 0:
                                    continue
                                else:
                                    sub_indicator['sub_list_filtered'].append(sub_sub_ind)
                        else:
                            for sub_sub_ind in sub_indicator['sub_list']:
                                if sub_sub_ind['cumulative'] == '0' or sub_sub_ind['cumulative'] == 0:
                                    continue
                                else:
                                    filtered_list.append(sub_sub_ind)
        else:
            filtered_list = master_indicators

        t_months = []
        if selected_months is not None and len(selected_months) > 0:
            for mon in selected_months:
                t_months.append((mon, datetime.date(2008, int(mon), 1).strftime('%B')))
        else:
            if int(reporting_year) == current_year:
                display_live = True
                if current_month == 1:
                    t_months.append((1, datetime.date(2008, 1, 1).strftime('%B')))
                if current_month >= 2 :
                    for i in range(1, current_month):
                        t_months.append((i, datetime.date(2008, i, 1).strftime('%B')))
                # if current_month > 4 :
                #     for i in range(current_month - 3, current_month):
                #         months.append((i, datetime.date(2008, i, 1).strftime('%B')))
            else:
                display_live = False
                for i in range(1, 13):
                    t_months.append((i, datetime.date(2008, i, 1).strftime('%B')))

        return {
            'selected_partners': selected_partners,
            'selected_governorates': selected_governorates,
            'selected_months': selected_months,
            'support_covid':int(support_covid),
            'month': month,
            'year': today.year,
            'month_name': month_name,
            'month_number': month_number,
            't_months': t_months,
            'database': database,
            'partners': partners,
            'governorates': governorates,
            'months': months,
            'master_indicators': filtered_list,
            'partner_info': partner_info,
            'selected_filter': selected_filter,
            'reporting_year': str(reporting_year),
            'display_live': display_live,
            'current_month': current_month,
            'current_month_name':  datetime.datetime.now().strftime("%B")
        }


class ReportCrisisViewOld(TemplateView):
    template_name = 'activityinfo/report_crisis_old.html'

    def get_context_data(self, **kwargs):

        ai_id = int(self.request.GET.get('ai_id', 0))
        database = Database.objects.get(ai_id=ai_id)
        selected_partners = self.request.GET.getlist('partners', [])
        selected_months = self.request.GET.getlist('months', [])
        selected_partner_name = self.request.GET.get('partner_name', 'All Partners')
        selected_governorates = self.request.GET.getlist('governorates', [])
        selected_governorate_name = self.request.GET.get('governorate_name', 'All Governorates')
        selected_sections = self.request.GET.getlist('sections',[])
        selected_type = self.request.GET.get('filter_type', '')

        current_month = date.today().month

        selected_filter = False

        reporting_year = database.reporting_year.year

        if selected_partners or selected_governorates or selected_months or selected_sections:
            selected_filter = True

        partners = get_partners_list(database)
        governorates = get_governorates_list(database)
        sections = get_reporting_sections_list(database)

        master_indicators = Indicator.objects.filter(activity__database=database).exclude(type='quality')\
            .order_by('sequence')

        if len(selected_type) > 0:
            master_indicators = master_indicators.filter(tag_focus__label=selected_type)

        master_indicators = master_indicators.filter(Q(master_indicator=True) |
                                                     Q(sub_indicators__isnull=True, individual_indicator=True))\
            .values(
            'id',
            'ai_id',
            'name',
            'master_indicator',
            'master_indicator_sub',
            'master_indicator_sub_sub',
            'individual_indicator',
            'awp_code',
            'measurement_type',
            'units',
            'cumulative_values',
            'values_partners_gov',
            'values_partners',
            'values_gov',
            'values',
            'is_cumulative',
            'activity',
            'tag_focus__label',
            'hpm_global_indicator',
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

        ).distinct()

        covid_indicators = Indicator.objects.filter(support_COVID=True).exclude(is_imported=True).values(
            'id',
            'ai_id',
            'name',
            'master_indicator',
            'master_indicator_sub',
            'master_indicator_sub_sub',
            'individual_indicator',
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
            'is_cumulative',
            'activity',
            'tag_focus',
            'tag_focus__label',
            'hpm_global_indicator',
        ).distinct()

        start_month = 4   # used to get cumulative values starting this month for covid reporting

        months = []
        if selected_months is not None and len(selected_months) > 0:
            for mon in selected_months:
                months.append((mon, calendar.month_abbr[int(mon)]))
        else:
            for i in range(1, current_month+1):
                months.append((i, calendar.month_abbr[i]))

        sliced_months = months[3:]

        return {
            # 'reports': report.order_by('id'),
            'database': database,
            'reporting_year': str(reporting_year),
            'current_month_name':  datetime.datetime.now().strftime("%B"),
            'months': months,
            'sliced_months': sliced_months,
            'partners': partners,
            'governorates': governorates,
            'indicators': master_indicators,
            'covid_indicators': covid_indicators,
            'selected_filter': selected_filter,
            'selected_partners': selected_partners,
            'selected_partner_name': selected_partner_name,
            'selected_governorates': selected_governorates,
            'selected_governorate_name': selected_governorate_name,
            'selected_months': selected_months,
            'sections': sections,
            'selected_sections': selected_sections,
            'selected_type': selected_type,
            'start_month':start_month
        }


class ReportCrisisView(TemplateView):
    template_name = 'activityinfo/report_crisis.html'

    def get_context_data(self, **kwargs):

        ai_id = int(self.request.GET.get('ai_id', 0))
        database = Database.objects.get(ai_id=ai_id)
        selected_partners = self.request.GET.getlist('partners', [])
        selected_months = self.request.GET.getlist('months', [])
        selected_governorates = self.request.GET.getlist('governorates', [])
        selected_sections = self.request.GET.getlist('sections',[])
        selected_type = self.request.GET.get('filter_type', '')

        current_month = date.today().month
        selected_filter = False
        reporting_year = database.reporting_year.year
        months = []
        if selected_partners or selected_governorates or selected_months or selected_sections:
            selected_filter = True
            partners = get_partners_list(database,selected_sections,selected_governorates,selected_months)
            governorates = get_governorates_list(database,selected_sections,selected_partners,selected_months)
            sections = get_reporting_sections_list(database,selected_partners,selected_governorates,selected_months)
            if selected_months is not None and len(selected_months) > 0:
                for mon in selected_months:
                    months.append((mon, calendar.month_name[int(mon)]))
            else:
                months = get_months_list(database, selected_partners, selected_governorates, selected_sections)
        else:
            partners = get_partners_list(database)
            governorates = get_governorates_list(database)
            sections = get_reporting_sections_list(database)
            # if selected_months is not None and len(selected_months) > 0:
            #     for mon in selected_months:
            #         months.append((mon, calendar.month_abbr[int(mon)]))
            # else:
            for i in range(1, current_month + 1):
                months.append((i, calendar.month_name[i]))
            # sliced_months = months[3:]

        all_indicators = Indicator.objects.filter(activity__database=database).exclude(type='quality')\
            .order_by('sequence')

        imported_indicators =Indicator.objects.filter(activity__database__support_covid=True).exclude(type='quality')
        mixed_indicators = all_indicators | imported_indicators

        master_indicators = all_indicators.filter(Q(master_indicator=True) |Q(sub_indicators__isnull=True,
                                                                                 individual_indicator=True))\
            .values(
            'id',
            'ai_id',
            'name',
            'master_indicator',
            'master_indicator_sub',
            'individual_indicator',
            'awp_code',
            'measurement_type',
            'units',
            'activity',
            'tag_focus__label',
            'hpm_global_indicator',
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
            'sub_indicators'
        ).order_by('id').distinct('id')

        if len(selected_type) > 0:
            master_indicators = master_indicators.filter(tag_focus__label=selected_type)

        for master_ind in master_indicators:
            master_ind['cumulative'] = get_indicator_cumulative_months_sections(master_ind, selected_months,
                                                                          selected_partners, selected_governorates,
                                                                          selected_sections)
            sub_indicators = get_sub_indicators_crisis_data(master_ind['id'],mixed_indicators)
            master_ind['sub_list'] = sub_indicators
            master_ind['sub_list_filtered'] = sub_indicators
            for ind in sub_indicators:
                if ind['master_indicator'] and not ind['is_imported']:
                    ind['cumulative'] = 0
                    continue
                if ind['is_imported']:
                    if len(selected_sections) > 0:
                        for section in selected_sections:
                            if '/' in section:
                                var1 = section.split('/')[0]
                                var2 = section.split('/')[1]
                                if var1 in ind['activity__database__label'] or var2 in ind[
                                    'activity__database__label']:
                                    ind['cumulative'] = get_indicator_cumulative_months_sections(ind, selected_months,
                                                                                             selected_partners,
                                                                                             selected_governorates)
                            elif ind['activity__database__label'] == section:
                                ind['cumulative'] = get_indicator_cumulative_months_sections(ind, selected_months,
                                         selected_partners, selected_governorates)
                            else:
                                ind['cumulative'] = 0
                    else:
                        ind['cumulative'] = get_indicator_cumulative_months_sections(ind, selected_months,
                                                                                     selected_partners,
                                                                                     selected_governorates,
                                                                                     )
                else:
                    ind['cumulative'] = get_indicator_cumulative_months_sections(ind, selected_months,
                                                                                 selected_partners,
                                                                                 selected_governorates,
                                                                                 selected_sections)
                sub_sub_indicators = get_sub_indicators_crisis_data(ind['id'],mixed_indicators)
                ind['sub_list'] = sub_sub_indicators
                ind['sub_list_filtered'] = sub_sub_indicators
                for ind_sub in sub_sub_indicators:
                    if ind_sub['master_indicator']:
                        ind_sub['cumulative'] = 0
                        continue
                    if ind['is_imported']:
                        if len(selected_sections) > 0:
                            for section in selected_sections:
                                if '/' in section:
                                    var1 = section.split('/')[0]
                                    var2 = section.split('/')[1]
                                    if var1 in ind_sub['activity__database__label']  or var2 in ind_sub[
                                        'activity__database__label']:
                                        ind_sub['cumulative'] = get_indicator_cumulative_months_sections(ind_sub,
                                                                                                     selected_months,
                                                                                                     selected_partners,
                                                                                                     selected_governorates)
                                elif ind_sub['activity__database__label'] == section:
                                        ind_sub['cumulative'] = get_indicator_cumulative_months_sections(ind_sub,
                                                                                                     selected_months,
                                                                                                     selected_partners,
                                                                                                    selected_governorates
                                                                                                    )
                                else:
                                    ind_sub['cumulative'] = 0
                        else:
                            ind_sub['cumulative'] = get_indicator_cumulative_months_sections(ind_sub,
                                                                                     selected_months,
                                                                                     selected_partners,
                                                                                     selected_governorates,
                                                                                     )

                    else:
                        ind_sub['cumulative'] = get_indicator_cumulative_months_sections(ind_sub, selected_months,
                                                                                     selected_partners,
                                                                                     selected_governorates,
                                                                                     selected_sections)
                    indicators = get_sub_indicators_crisis_data(ind_sub['id'],mixed_indicators)
                    ind_sub['sub_list'] = indicators
                    ind_sub['sub_list_filtered'] = indicators
                    for item in indicators:
                        if item['master_indicator']:
                            item['cumulative'] = 0
                            continue
                        if ind['is_imported']:
                            if len(selected_sections) > 0:
                                for section in selected_sections:
                                    if '/' in section:
                                        var1 = section.split('/')[0]
                                        var2 = section.split('/')[1]
                                        if var1 in item['activity__database__label'] or var2 in item[
                                            'activity__database__label']:
                                            item['cumulative'] = get_indicator_cumulative_months_sections(item,
                                                                                                          selected_months,
                                                                                                          selected_partners,
                                                                                                          selected_governorates)
                                    elif item['activity__database__label'] == section:
                                        item['cumulative'] = get_indicator_cumulative_months_sections(item,
                                                                                                      selected_months,
                                                                                                      selected_partners,
                                                                                                      selected_governorates)
                                    else:
                                        item['cumulative'] = 0
                            else:
                                item['cumulative'] = get_indicator_cumulative_months_sections(item, selected_months,
                                                                                              selected_partners,
                                                                                              selected_governorates,
                                                                                              )
                        else:
                            item['cumulative'] = get_indicator_cumulative_months_sections(item, selected_months,
                                                                                          selected_partners,
                                                                                          selected_governorates,
                                                                                          selected_sections)
        filtered_list=[]
        if selected_filter:
            for master_ind in master_indicators:
                if not (master_ind['cumulative'] == '0' or master_ind['cumulative'] == 0):
                    filtered_list.append(master_ind)
                    master_ind['sub_list_filtered'] =[]
                    for sub_indicator in master_ind['sub_list']:
                        sub_indicator['sub_list_filtered'] = []
                        if not (sub_indicator['cumulative'] == '0' or sub_indicator['cumulative'] == 0):
                            master_ind['sub_list_filtered'].append(sub_indicator)
                        for sub_sub_ind in sub_indicator['sub_list']:
                            if sub_sub_ind['cumulative'] == '0' or sub_sub_ind['cumulative'] == 0 :
                                continue
                            else:
                                sub_indicator['sub_list_filtered'].append(sub_sub_ind)
                else:
                    for sub_indicator in master_ind['sub_list']:
                        if not (sub_indicator['cumulative'] == '0' or sub_indicator['cumulative'] == 0):
                            filtered_list.append(sub_indicator)
                            sub_indicator['sub_list_filtered']=[]
                            for sub_sub_ind in sub_indicator['sub_list']:
                                if sub_sub_ind['cumulative'] == '0' or sub_sub_ind['cumulative'] == 0 :
                                    continue
                                else:
                                    sub_indicator['sub_list_filtered'].append(sub_sub_ind)
                        else:
                            for sub_sub_ind in sub_indicator['sub_list']:
                                if sub_sub_ind['cumulative'] == '0' or sub_sub_ind['cumulative'] == 0:
                                    continue
                                else:
                                    filtered_list.append(sub_sub_ind)
        else:
            filtered_list = master_indicators

        covid_indicators = imported_indicators.filter(support_COVID=True).filter(master_indicator=True).exclude(is_imported=True).values(
            'id',
            'ai_id',
            'name',
            'master_indicator',
            'master_indicator_sub',
            'master_indicator_sub_sub',
            'individual_indicator',
            'awp_code',
            'measurement_type',
            'units',
            'category',
            'cumulative_values',
            'values_partners_gov',
            'values_partners',
            'values_gov',
            'values',
            'activity',

        ).distinct()

        start_month = 4  # used to get cumulative values starting this month for covid reporting
        filtered_covid_indicators =[]

        if len(selected_sections) > 0:
            for section in selected_sections:
                if '/' in section:
                    section = section.split('/')
                    filtered =list(covid_indicators.filter(Q(activity__database__label__contains=section[0]) | Q(activity__database__label__contains=section[1])))
                    for item in filtered:
                        filtered_covid_indicators.append(item)
                else:
                    filtered= list(covid_indicators.filter(activity__database__label__contains=section))
                    for item in filtered:
                        filtered_covid_indicators.append(item)
        else:
            filtered_covid_indicators = covid_indicators

        for master_ind in filtered_covid_indicators:
            master_ind['cumulative'] = get_indicator_cumulative_months(master_ind, selected_months,
                                                                            selected_partners,
                                                                            selected_governorates,
                                                                            start_month)
            sub_indicators = get_sub_indicators_data_new(master_ind['id'], imported_indicators)
            master_ind['sub_list'] = sub_indicators
            master_ind['sub_list_filtered'] = sub_indicators
            for ind in sub_indicators:
                ind['cumulative'] = get_indicator_cumulative_months(ind, selected_months,
                                                                             selected_partners,
                                                                            selected_governorates,
                                                                            start_month
                                                                             )
                sub_sub_indicators = get_sub_indicators_data_new(ind['id'], imported_indicators)
                ind['sub_list'] = sub_sub_indicators
                ind['sub_list_filtered'] = sub_sub_indicators
                for sub_ind in sub_sub_indicators:
                    sub_ind['cumulative'] = get_indicator_cumulative_months(sub_ind, selected_months,
                                                                                 selected_partners,
                                                                                 selected_governorates,
                                                                                 start_month)
                    indicators = get_sub_indicators_data_new(sub_ind['id'],imported_indicators)
                    sub_ind['sub_list'] = indicators
                    sub_ind['sub_list_filtered'] = indicators
        covid_filtered_list=[]
        if selected_filter:
            for master_ind in filtered_covid_indicators:
                if not (master_ind['cumulative'] == '0' or master_ind['cumulative'] == 0):
                    covid_filtered_list.append(master_ind)
                    master_ind['sub_list_filtered'] = []
                    for sub_indicator in master_ind['sub_list']:
                        sub_indicator['sub_list_filtered'] = []
                        if not (sub_indicator['cumulative'] == '0' or sub_indicator['cumulative'] == 0):
                            master_ind['sub_list_filtered'].append(sub_indicator)
                        for sub_sub_ind in sub_indicator['sub_list']:
                            if sub_sub_ind['cumulative'] == '0' or sub_sub_ind['cumulative'] == 0:
                                continue
                            else:
                                sub_indicator['sub_list_filtered'].append(sub_sub_ind)
                else:
                    for sub_indicator in master_ind['sub_list']:
                        if not (sub_indicator['cumulative'] == '0' or sub_indicator['cumulative'] == 0):
                            covid_filtered_list.append(sub_indicator)
                            sub_indicator['sub_list_filtered'] = []
                            for sub_sub_ind in sub_indicator['sub_list']:
                                if sub_sub_ind['cumulative'] == '0' or sub_sub_ind['cumulative'] == 0:
                                    continue
                                else:
                                    sub_indicator['sub_list_filtered'].append(sub_sub_ind)
                        else:
                            for sub_sub_ind in sub_indicator['sub_list']:
                                if sub_sub_ind['cumulative'] == '0' or sub_sub_ind['cumulative'] == 0:
                                    continue
                                else:
                                    covid_filtered_list.append(sub_sub_ind)
        else:
            covid_filtered_list = filtered_covid_indicators




        return {
            # 'reports': report.order_by('id'),
            'database': database,
            'reporting_year': str(reporting_year),
            'current_month_name':  datetime.datetime.now().strftime("%B"),
            'months': months,
            # 'sliced_months': sliced_months,
            'partners': partners,
            'governorates': governorates,
            'sections': sections,
            'indicators': filtered_list,
            'covid_indicators': covid_filtered_list,
            'selected_filter':selected_filter ,
            'selected_partners': selected_partners,
            'selected_governorates': selected_governorates,
            'selected_months': selected_months,
            'selected_sections': selected_sections,
            'selected_type': selected_type,
            'start_month':start_month
        }


class ReportLiveCrisis(TemplateView):
    template_name = 'activityinfo/report_crisis_live.html'

    def get_context_data(self,**kwargs):
        ai_id = int(self.request.GET.get('ai_id', 0))
        database = Database.objects.get(ai_id=ai_id)
        selected_partners = self.request.GET.getlist('partners', [])

        selected_governorates = self.request.GET.getlist('governorates', [])
        selected_sections = self.request.GET.getlist('sections', [])
        selected_type = self.request.GET.get('filter_type', '')
        selected_filter = False

        today = datetime.date.today()
        day_number = today.strftime("%d")
        month_number = today.strftime("%m")
        month = int(today.strftime("%m"))
        month_name = calendar.month_name[month]

        reporting_year = database.reporting_year.year
        # report = LiveActivityReport.objects.filter(database_id=database.ai_id)

        if selected_partners or selected_governorates  or selected_sections:
            selected_filter = True
            partners = get_partners_list(database,sections=selected_sections,govs=selected_governorates,report_type='live')
            governorates = get_governorates_list(database,sections=selected_sections,partners=selected_partners,report_type='live')
            sections = get_reporting_sections_list(database,partners=selected_partners,govs=selected_governorates,report_type='live')
        else:
            partners = get_partners_list(database,report_type='live')
            governorates = get_governorates_list(database, report_type='live')
            sections = get_reporting_sections_list(database, report_type='live')

        all_indicators = Indicator.objects.filter(activity__database=database).exclude(type='quality') \
            .order_by('sequence')

        imported_indicators = Indicator.objects.filter(activity__database__support_covid=True).exclude(type='quality')
        mixed_indicators = all_indicators | imported_indicators

        master_indicators = all_indicators.filter(Q(master_indicator=True) | Q(sub_indicators__isnull=True,
                                                                               individual_indicator=True)) \
            .values(
            'id',
            'ai_id',
            'name',
            'master_indicator',
            'master_indicator_sub',
            'individual_indicator',
            'awp_code',
            'measurement_type',
            'units',
            'activity',
            'tag_focus__label',
            'hpm_global_indicator',
            'category',
            'values_sections_live',
            'values_sections_partners_live',
            'values_sections_gov_live',
            'values_sections_partners_gov_live',
            'values_crisis_live',
            'values_crisis_gov_live',
            'values_crisis_partners_live',
            'values_crisis_partners_gov_live',
            'values_crisis_cumulative_live',
            'sub_indicators'
        ).order_by('id').distinct('id')

        if len(selected_type) > 0:
            master_indicators = master_indicators.filter(tag_focus__label=selected_type)

        for master_ind in master_indicators:
            master_ind['cumulative'] = get_indicator_live_cumulative_section(master_ind, month,
                                                                                selected_partners,
                                                                                selected_governorates,
                                                                                selected_sections)
            sub_indicators = get_sub_indicators_live_crisis_data(master_ind['id'], mixed_indicators)
            master_ind['sub_list'] = sub_indicators
            master_ind['sub_list_filtered'] = sub_indicators
            for ind in sub_indicators:
                if ind['master_indicator'] and not ind['is_imported']:
                    ind['cumulative'] = 0
                    continue
                if ind['is_imported']:
                    if len(selected_sections) > 0:
                        for section in selected_sections:
                            if '/' in section:
                                var1 = section.split('/')[0]
                                var2 = section.split('/')[1]
                                if var1 in ind['activity__database__label'] or var2 in ind[
                                    'activity__database__label']:
                                    ind['cumulative'] = get_indicator_live_cumulative_section(ind, month,
                                                                                                 selected_partners,
                                                                                                 selected_governorates)
                            elif ind['activity__database__label'] == section:
                                    ind['cumulative'] = get_indicator_live_cumulative_section(ind, month,
                                                                                                 selected_partners,
                                                                                                 selected_governorates)
                            else:
                                ind['cumulative'] = 0
                    else:
                        ind['cumulative'] = get_indicator_live_cumulative_section(ind, month,
                                                                                     selected_partners,
                                                                                     selected_governorates,
                                                                                     )
                else:
                    ind['cumulative'] = get_indicator_live_cumulative_section(ind, month,
                                                                                 selected_partners,
                                                                                 selected_governorates,
                                                                                 selected_sections)
                sub_sub_indicators = get_sub_indicators_live_crisis_data(ind['id'], mixed_indicators)
                ind['sub_list'] = sub_sub_indicators
                ind['sub_list_filtered'] = sub_sub_indicators
                for ind_sub in sub_sub_indicators:
                    if ind_sub['master_indicator']:
                        ind_sub['cumulative'] = 0
                        continue
                    if ind['is_imported']:
                        if len(selected_sections) > 0:
                            for section in selected_sections:
                                if '/' in section:
                                    var1 = section.split('/')[0]
                                    var2 = section.split('/')[1]
                                    if var1 in ind_sub['activity__database__label'] or var2 in ind_sub[
                                        'activity__database__label']:
                                        ind_sub['cumulative'] = get_indicator_live_cumulative_section(ind_sub,
                                                                                                         month,
                                                                                                         selected_partners,
                                                                                                         selected_governorates)
                                elif ind_sub['activity__database__label'] == section:
                                        ind_sub['cumulative'] = get_indicator_live_cumulative_section(ind_sub,
                                                                                                         month,
                                                                                                         selected_partners,
                                                                                                          selected_governorates)
                                else:
                                    ind_sub['cumulative'] = 0
                        else:
                            ind_sub['cumulative'] = get_indicator_live_cumulative_section(ind_sub, month,
                                                                                             selected_partners,
                                                                                             selected_governorates,
                                                                                             )
                    else:
                        ind_sub['cumulative'] = get_indicator_live_cumulative_section(ind_sub, month,
                                                                                         selected_partners,
                                                                                         selected_governorates,
                                                                                         selected_sections)
                    indicators = get_sub_indicators_live_crisis_data(ind_sub['id'], mixed_indicators)
                    ind_sub['sub_list'] = indicators
                    ind_sub['sub_list_filtered'] = indicators
                    for item in indicators:
                        if item['master_indicator']:
                            item['cumulative'] = 0
                            continue
                        if ind['is_imported']:
                            if len(selected_sections) > 0:
                                for section in selected_sections:
                                    if '/' in section:
                                        var1 = section.split('/')[0]
                                        var2 = section.split('/')[1]
                                        if var1 in item['activity__database__label'] or var2 in item[
                                            'activity__database__label']:
                                            item['cumulative'] = get_indicator_live_cumulative_section(item,
                                                                                                          month,
                                                                                                          selected_partners,
                                                                                                          selected_governorates)
                                    elif item['activity__database__label'] == section:
                                        item['cumulative'] = get_indicator_live_cumulative_section(item,
                                                                                                      month,
                                                                                                      selected_partners,
                                                                                                      selected_governorates)
                                    else:
                                        item['cumulative'] = 0
                            else:
                                item['cumulative'] = get_indicator_live_cumulative_section(item, month,
                                                                                              selected_partners,
                                                                                              selected_governorates,
                                                                                              )
                        else:
                            item['cumulative'] = get_indicator_live_cumulative_section(item, month,
                                                                                          selected_partners,
                                                                                          selected_governorates,
                                                                                          selected_sections)

        filtered_list = []
        if selected_filter:
            for master_ind in master_indicators:
                if not (master_ind['cumulative'] == '0' or master_ind['cumulative'] == 0):
                    filtered_list.append(master_ind)
                    master_ind['sub_list_filtered'] = []
                    for sub_indicator in master_ind['sub_list']:
                        sub_indicator['sub_list_filtered'] = []
                        if not (sub_indicator['cumulative'] == '0' or sub_indicator['cumulative'] == 0):
                            master_ind['sub_list_filtered'].append(sub_indicator)
                        for sub_sub_ind in sub_indicator['sub_list']:
                            if sub_sub_ind['cumulative'] == '0' or sub_sub_ind['cumulative'] == 0:
                                continue
                            else:
                                sub_indicator['sub_list_filtered'].append(sub_sub_ind)
                else:
                    for sub_indicator in master_ind['sub_list']:
                        if not (sub_indicator['cumulative'] == '0' or sub_indicator['cumulative'] == 0):
                            filtered_list.append(sub_indicator)
                            sub_indicator['sub_list_filtered'] = []
                            for sub_sub_ind in sub_indicator['sub_list']:
                                if sub_sub_ind['cumulative'] == '0' or sub_sub_ind['cumulative'] == 0:
                                    continue
                                else:
                                    sub_indicator['sub_list_filtered'].append(sub_sub_ind)
                        else:
                            for sub_sub_ind in sub_indicator['sub_list']:
                                if sub_sub_ind['cumulative'] == '0' or sub_sub_ind['cumulative'] == 0:
                                    continue
                                else:
                                    filtered_list.append(sub_sub_ind)
        else:
            filtered_list = master_indicators

        covid_indicators = imported_indicators.filter(support_COVID=True).filter(master_indicator=True).exclude(
            is_imported=True).values(
                'id',
                'ai_id',
                'name',
                'master_indicator',
                'master_indicator_sub',
                'individual_indicator',
                'awp_code',
                'measurement_type',
                'units',
                'category',
                'values_live',
                'values_gov_live',
                'values_partners_live',
                'values_partners_gov_live',
                'cumulative_values_live',
                'activity',

        ).distinct()

        start_month = 4  # used to get cumulative values starting this month for covid reporting
        filtered_covid_indicators = []
        if len(selected_sections) > 0:
            for section in selected_sections:
                if '/' in section:
                    section = section.split('/')
                    filtered = list(covid_indicators.filter(Q(activity__database__label__contains=section[0]) | Q(
                        activity__database__label__contains=section[1])))
                    for item in filtered:
                        filtered_covid_indicators.append(item)
                else:
                    filtered = list(covid_indicators.filter(activity__database__label__contains=section))
                    for item in filtered:
                        filtered_covid_indicators.append(item)
        else:
            filtered_covid_indicators = covid_indicators

        for master_ind in filtered_covid_indicators:
            master_ind['cumulative'] = get_indicator_live_cumulative(master_ind, month,
                                                                       selected_partners,
                                                                       selected_governorates,
                                                                       start_month)
            sub_indicators = get_sub_indicators_live_data(master_ind['id'], imported_indicators)
            master_ind['sub_list'] = sub_indicators
            master_ind['sub_list_filtered'] = sub_indicators
            for ind in sub_indicators:
                ind['cumulative'] = get_indicator_live_cumulative(ind, month,
                                                                    selected_partners,
                                                                    selected_governorates,
                                                                    start_month
                                                                    )
                sub_sub_indicators = get_sub_indicators_live_data(ind['id'], imported_indicators)
                ind['sub_list'] = sub_sub_indicators
                ind['sub_list_filtered'] = sub_sub_indicators
                for sub_ind in sub_sub_indicators:
                    sub_ind['cumulative'] = get_indicator_live_cumulative(sub_ind, month,
                                                                            selected_partners,
                                                                            selected_governorates,
                                                                            start_month)
                    indicators = get_sub_indicators_live_data(sub_ind['id'], imported_indicators)
                    sub_ind['sub_list'] = indicators
                    sub_ind['sub_list_filtered'] = indicators
        covid_filtered_list = []
        if selected_filter:
            for master_ind in filtered_covid_indicators:
                if not (master_ind['cumulative'] == '0' or master_ind['cumulative'] == 0):
                    covid_filtered_list.append(master_ind)
                    master_ind['sub_list_filtered'] = []
                    for sub_indicator in master_ind['sub_list']:
                        sub_indicator['sub_list_filtered'] = []
                        if not (sub_indicator['cumulative'] == '0' or sub_indicator['cumulative'] == 0):
                            master_ind['sub_list_filtered'].append(sub_indicator)
                        for sub_sub_ind in sub_indicator['sub_list']:
                            if sub_sub_ind['cumulative'] == '0' or sub_sub_ind['cumulative'] == 0:
                                continue
                            else:
                                sub_indicator['sub_list_filtered'].append(sub_sub_ind)
                else:
                    for sub_indicator in master_ind['sub_list']:
                        if not (sub_indicator['cumulative'] == '0' or sub_indicator['cumulative'] == 0):
                            covid_filtered_list.append(sub_indicator)
                            sub_indicator['sub_list_filtered'] = []
                            for sub_sub_ind in sub_indicator['sub_list']:
                                if sub_sub_ind['cumulative'] == '0' or sub_sub_ind['cumulative'] == 0:
                                    continue
                                else:
                                    sub_indicator['sub_list_filtered'].append(sub_sub_ind)
                        else:
                            for sub_sub_ind in sub_indicator['sub_list']:
                                if sub_sub_ind['cumulative'] == '0' or sub_sub_ind['cumulative'] == 0:
                                    continue
                                else:
                                    covid_filtered_list.append(sub_sub_ind)
        else:
            covid_filtered_list = filtered_covid_indicators
        return {

            'database': database,
            'reporting_year': str(reporting_year),
            'current_month_name': datetime.datetime.now().strftime("%B"),
            'partners': partners,
            'governorates': governorates,
            'indicators': filtered_list,
            'covid_indicators': covid_filtered_list,
            'selected_filter': selected_filter,
            'selected_partners': selected_partners,
            'selected_governorates': selected_governorates,
            'month': month,
            'month_name': month_name,
            'month_number': month_number,
            'day_number':day_number,
            'sections':sections,
            'selected_sections':selected_sections,
            'selected_type': selected_type,
            'start_month':start_month
        }


class ReportInternalView(TemplateView):
    template_name = 'activityinfo/report_internal.html'

    def get_context_data(self, **kwargs):
        ai_id = int(self.request.GET.get('ai_id', 0))
        database = Database.objects.get(ai_id=ai_id)
        reporting_year = database.reporting_year.year
        report = ActivityReport.objects.filter(database_id=database.ai_id)
        none_ai_indicators = Indicator.objects.filter(none_ai_indicator=True,activity__database=database).values(
            'id',
            'ai_id',
            'name',
            'master_indicator',
            'master_indicator_sub',
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
            'is_cumulative',
            'type'
        ).distinct()

        db_url =""
        if database.reporting_year.name == '2020_Crisis':
            db_url = '/activityinfo/report-crisis'
        else:
            db_url= '/activityinfo/report'

        months = []
        for i in range(1, 13):
            months.append((i, calendar.month_abbr[i]))
        return {
            'reports': report.order_by('id'),
            'database': database,
            'reporting_year': str(reporting_year),
            'current_month_name': datetime.datetime.now().strftime("%B"),
            'list_indicators':none_ai_indicators,
            'months':months,
            'db_url': str(db_url),
        }


class ReportInternalFormView(TemplateView):
    template_name = 'activityinfo/report_internal_form.html'

    def get_context_data(self, **kwargs):

        indicator_id = self.request.GET.get('id', 0)
        ai_id = self.request.GET.get('ai_id', 0)
        step = int(self.request.GET.get('step', 0))
        database = Database.objects.get(ai_id=ai_id)
        reporting_year = database.reporting_year.year
        activities = Activity.objects.filter(database=database.id)
        report = ActivityReport.objects.filter(database_id=database.ai_id,indicator_id=indicator_id).values(
            'indicator_id',
            'indicator_name',
            'indicator_units',
            'indicator_value',
            'location_adminlevel_governorate_code',
            'location_adminlevel_governorate',
            'database_id',
            'start_date',
            'month'
            )
        governorates=[]
        governorates.append((2,'Akkar'))
        governorates.append((3,' Baalbek_Hermel'))
        governorates.append((4,'North'))
        governorates.append((5,'Mount Lebanon'))
        governorates.append((6,'Bekaa'))
        governorates.append((7,'Beirut'))
        governorates.append((8,'South'))
        governorates.append((9,'Nabatiye'))
        governorates.append((10, 'National'))

        if indicator_id != 0:
            indicator = Indicator.objects.get(id=indicator_id)
        else:
            step=1
            indicator = None
        months =[]
        for i in range(1,13):
            months.append((i,calendar.month_name[i]))
        db_url = ""
        if database.reporting_year.name == '2020_Crisis':
            db_url = '/activityinfo/report-crisis'
        else:
            db_url = '/activityinfo/report'
        return {
            'reports': report.order_by('id'),
            'database': database,
            'reporting_year': str(reporting_year),
            'current_month_name': datetime.datetime.now().strftime("%B"),
            'activities':activities,
            'governorates':governorates,
            'indicator':indicator,
            'step':step,
            'months':months,
            'db_url':db_url
        }

    def post(self, request, *args, **kwargs):
        form_name = self.request.POST.get('form_name', 0)
        indicator_id = self.request.POST.get('id', 0)
        ai_id = self.request.POST.get('ai_id', 0)
        database = Database.objects.get(ai_id=ai_id)
        step = 0

        if indicator_id:
            indicator = Indicator.objects.get(id=indicator_id)
        else:
            step = 2
            indicator = Indicator(ai_indicator=None)
        gov = ""
        value = 0
        month = 0
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

        if form_name == 'valuesform':
            row_values = self.request.POST.get('row_values', "")
            json_string = json.loads(row_values)
            if 'myrows' in json_string:
                 ActivityReport.objects.filter(database_id=ai_id, indicator_id=indicator_id).delete()
                 indicator.values = {}
                 indicator.values_gov = {}
                 indicator.values_partners = {}
                 indicator.values_partners_gov = {}
                 indicator.cumulative_values = {}
            indicator.save()

            for row in json_string['myrows']:
                if 'Governorate' in row:
                    gov = row['Governorate']
                if 'Month' in row:
                    month = row['Month']
                if "Value" in row:
                    value = row['Value']

                gov_name=""
                for num , name in governorates:
                    if num == gov:
                        gov_name=name

                date = datetime.datetime.strptime(month, "%Y-%m")
                date = date.replace(day=01)

                report = ActivityReport()
                report.indicator_name = indicator.name
                report.indicator_id = indicator.id
                report.database_id = ai_id
                report.master_indicator = indicator.master_indicator
                report.master_indicator_sub = indicator.master_indicator_sub
                report.month = month
                report.start_date = date
                report.location_adminlevel_governorate_code = gov
                report.location_adminlevel_governorate = gov_name
                report.indicator_value = value
                report.indicator_units = indicator.units
                report.partner_label = 'UNICEF'
                report.partner_id = 'UNICEF'
                report.funded_by = 'UNICEF'
                report.save()

            calculate_internal_indicators_values(ai_id,indicator_id)
            if database:
                calculate_internal_cumulative_results(database.id,indicator_id)

            return HttpResponseRedirect('/activityinfo/report-internal/?rep_year=2020&ai_id=' + str(ai_id))

        if form_name == 'resultsform':
            row_results = self.request.POST.get('row_results', "")
            json_string = json.loads(row_results)
            result=""
            gov=""
            indicator.results = {}
            indicator.save()
            results_list = {}
            if 'myrows' in json_string:
                for row in json_string['myrows']:
                    if 'Result' in row:
                        result = row['Result']
                    if 'Month' in row:
                        month = row['Month']
                    if "Governorate" in row:
                        gov = row['Governorate']

                    key = '{}-{}'.format(month,gov)
                    results_list[key] = result

                indicator.results = results_list
                indicator.save()

            return HttpResponseRedirect('/activityinfo/report-internal/?rep_year=2020&ai_id=' + str(ai_id))

        if form_name == 'indicatorform':
            name = self.request.POST.get('name', "")
            activity_id = self.request.POST.get('activity', "")
            awp_code = self.request.POST.get('awp_code',"")
            qualitative_target = self.request.POST.get('qualitative_target',"")
            unit = self.request.POST.get('unit',"")
            level = self.request.POST.get('level',"")
            type = self.request.POST.get('type',"")
            measurement = self.request.POST.get('measurement',"")
            activity = Activity.objects.get(id=activity_id)
            qualitative_result = self.request.POST.get('qualitative_result',"")
            status = self.request.POST.get('status',"")


            if self.request.POST.get('target'):
                target = self.request.POST.get('target', default=0)
            else:
                target=0

            if level == 'master_indicator':
                master_indicator = True
            else:
                master_indicator = False

            if level == 'sub_master_indicator':
                sub_master_indicator = True
            else:
                sub_master_indicator = False

            indicator.label = name
            indicator.name = name
            indicator.type = type
            indicator.activity = activity
            indicator.units = unit
            indicator.master_indicator = master_indicator
            indicator.awp_code = awp_code
            indicator.master_indicator_sub = sub_master_indicator
            indicator.none_ai_indicator = True
            indicator.target = target
            indicator.qualitative_target = qualitative_target
            indicator.qualitative_result = qualitative_result
            indicator.status = status
            indicator.measurement_type = measurement
            indicator.funded_by = 'UNICEF'
            indicator.save()

            return HttpResponseRedirect('/activityinfo/report-internal-form/?rep_year=2020&ai_id='+str(ai_id)+'&id='+str(indicator.id)+'&step='+str(step))


class ReportPartnerView(TemplateView):
    template_name = 'activityinfo/report_partner.html'

    def get_context_data(self, **kwargs):

        selected_filters = False
        today = datetime.date.today()
        first = today.replace(day=1)
        last_month = first - datetime.timedelta(days=1)
        month_number = last_month.strftime("%m")
        month = int(last_month.strftime("%m"))
        month_name = last_month.strftime("%B")

        selected_indicator = int(self.request.GET.get('indicator_id', 0))
        selected_sub_indicator = self.request.GET.getlist('sub_indicator_id', [])
        selected_governorate = self.request.GET.get('governorate', 0)
        selected_governorate_name = self.request.GET.get('governorate_name', 'All Governorates')
        selected_partner = self.request.GET.get('partner', "")
        selected_partner_name = self.request.GET.get('partners_name', 'All Partners')

        if selected_indicator or selected_governorate:
            selected_filters = True

        ai_id = int(self.request.GET.get('ai_id', 0))
        database = Database.objects.get(ai_id=ai_id)
        reporting_year = database.reporting_year.year

        if selected_indicator:
            indicator = Indicator.objects.get(id=selected_indicator)
            indicator = {
                'id': indicator.id,
                'ai_id': indicator.ai_id,
                'name': indicator.name,
                'ai_indicator':indicator.ai_indicator,
                'explication': indicator.explication,
                'awp_code': indicator.awp_code,
                'measurement_type': indicator.measurement_type,
                'units': indicator.units,
                'target': indicator.target,
                'status_color': indicator.status_color,
                'status': indicator.status,
                'cumulative_values': indicator.cumulative_values,
                'values_partners_gov': indicator.values_partners_gov,
                'values_partners': indicator.values_partners,
                'values_gov': indicator.values_gov,
                'values': indicator.values,
            }
            selected_indicator_name = indicator['name']
            partners_values = indicator['values_partners']
            partners_list=[]
            if partners_values:
                for key , value in partners_values.items():
                    p = key.split('-')[1]
                    if (p,p) not in partners_list:
                        partners_list.append((p,p))

        else:
            indicator = []
            selected_indicator_name = ""
            partners=[]
            governorates=[]
            partners_list=[]

        # report = ActivityReport.objects.filter(database_id=database.ai_id)
        #
        # if database.is_funded_by_unicef:
        #    report = report.filter(funded_by__contains='UNICEF')

        partners = get_partners_list(database)
        governorates = get_governorates_list(database)

        # partners = report.values('partner_label', 'partner_id').distinct()
        # governorates = report.values('location_adminlevel_governorate_code',
        #                              'location_adminlevel_governorate').distinct()

        master_indicators = Indicator.objects.filter(activity__database=database, master_indicator=True).exclude(
            is_sector=True).order_by('sequence')
        individual_indicators = Indicator.objects.filter(activity__database=database,
                                                         individual_indicator=True).exclude(is_sector=True).order_by('sequence')
        indicators = master_indicators | individual_indicators
        indicators = indicators.values(
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
        selected_sub_indicator = [int(x) for x in selected_sub_indicator]

        list_selected_sub = Indicator.objects.filter(id__in=selected_sub_indicator)
        list_selected_sub = list_selected_sub.values(
            'id',
            'ai_id',
            'name',
            'units',
            'target',
            'measurement_type',
            'cumulative_values',
            'values_partners_gov',
            'values_partners',
            'values_gov',
            'values',
        )
        months = []
        for i in range(1, 13):
            months.append((i, datetime.date(2008, i, 1).strftime('%B')))

        # if selected_governorate is not None:
        #     for x in governorates:
        #         if x["location_adminlevel_governorate_code"] == selected_governorate:
        #             selected_governorate_name = x["location_adminlevel_governorate"]

        if selected_partner is not None and len(selected_partner) > 0:
            for x in partners:
                if x["partner_id"] == selected_partner:
                    selected_partner_name = x["partner_label"]


        return {
            # 'reports': report.order_by('id'),
            'month': month,
            'year': today.year,
            'month_name': month_name,
            'month_number': month_number,
            'months': months,
            'database': database,
            'partners': partners,
            'governorates': governorates,
            'indicators': indicators,
            'indicator': indicator,
            'selected_governorate': selected_governorate,
            'selected_governorate_name': selected_governorate_name,
            'selected_indicator': selected_indicator,
            'selected_sub_indicator': selected_sub_indicator,
            'selected_indicator_name': selected_indicator_name,
            'list_selected_sub': list_selected_sub,
            # 'locations': locations,
            'selected_filters': selected_filters,
            'current_month': datetime.datetime.now().strftime("%B"),
            'reporting_year': str(reporting_year),
            'selected_partner':selected_partner,
            'selected_partner_name':selected_partner_name,
            'partners_list':partners_list

        }


class ReportPartnerCrisisView(TemplateView):
    template_name = 'activityinfo/report_partner_crisis.html'

    def get_context_data(self, **kwargs):

        selected_filters = False
        today = datetime.date.today()
        first = today.replace(day=1)
        last_month = first - datetime.timedelta(days=1)
        month_number = last_month.strftime("%m")
        month = int(last_month.strftime("%m"))
        month_name = last_month.strftime("%B")

        selected_indicator = int(self.request.GET.get('indicator_id', 0))
        selected_sub_indicator = self.request.GET.getlist('sub_indicator_id', [])
        selected_governorate = self.request.GET.get('governorate', 0)
        selected_governorate_name = self.request.GET.get('governorate_name', 'All Governorates')
        selected_partner = self.request.GET.get('partner', "")
        selected_partner_name = self.request.GET.get('partners_name', 'All Partners')
        selected_section = self.request.GET.get('section', "")
        selected_section_name = self.request.GET.get('section_name', 'All Sections')

        if selected_indicator or selected_governorate or selected_section:
            selected_filters = True

        ai_id = int(self.request.GET.get('ai_id', 0))
        database = Database.objects.get(ai_id=ai_id)
        reporting_year = database.reporting_year.year

        if selected_indicator:
            indicator = Indicator.objects.get(id=selected_indicator)
            indicator = {
                'id': indicator.id,
                'ai_id': indicator.ai_id,
                'name': indicator.name,
                'ai_indicator':indicator.ai_indicator,
                'measurement_type': indicator.measurement_type,
                'units': indicator.units,
                'cumulative_values': indicator.cumulative_values,
                'values_cumulative_weekly': indicator.values_cumulative_weekly,
                'values_partners_gov_weekly': indicator.values_partners_gov_weekly,
                'values_partners_weekly': indicator.values_partners_weekly,
                'values_gov_weekly': indicator.values_gov_weekly,
                'values_weekly': indicator.values_weekly,
                'values_sections':indicator.values_sections,
                'values_sections_partners':indicator.values_sections_partners,
                'values_sections_partners_gov':indicator.values_sections_partners_gov,
                'values_sections_gov':indicator.values_sections_gov
            }
            selected_indicator_name = indicator['name']
            partners_list=[]
            if len(selected_section) > 0:
                partners_values = indicator['values_sections_partners']
                if partners_values:
                    for key, value in partners_values.items():
                        keys = key.split('-')
                        if keys[1] == selected_section:
                            p = keys[2]
                            if (p, p) not in partners_list:
                                partners_list.append((p, p))
            else:
                partners_values = indicator['values_partners_weekly']
                if partners_values:
                    for key, value in partners_values.items():
                        keys = key.split('-')
                        p = keys[1]
                        if (p, p) not in partners_list:
                            partners_list.append((p, p))
        else:
            indicator = []
            selected_indicator_name = ""
            partners=[]
            governorates=[]
            partners_list=[]

        # report = ActivityReport.objects.filter(database_id=database.ai_id)
        #
        # if database.is_funded_by_unicef:
        #    report = report.filter(funded_by__contains='UNICEF')

        partners = get_partners_list(database)
        governorates = get_governorates_list(database)
        sections = get_reporting_sections_list(database)

        # partners = report.values('partner_label', 'partner_id').distinct()
        # governorates = report.values('location_adminlevel_governorate_code',
        #                              'location_adminlevel_governorate').distinct()

        master_indicators = Indicator.objects.filter(activity__database=database, master_indicator=True).exclude(
            is_sector=True).order_by('sequence')
        individual_indicators = Indicator.objects.filter(activity__database=database,
                                                         individual_indicator=True).exclude(is_sector=True).order_by('sequence')
        indicators = master_indicators | individual_indicators
        indicators = indicators.values(
            'id',
            'ai_id',
            'name',
            'measurement_type',
            'units',
            'values_cumulative_weekly',
            'values_partners_gov_weekly',
            'values_partners_weekly',
            'values_gov_weekly',
            'values_weekly',
            'values_sections',
            'values_sections_partners',
            'values_sections_partners_gov',
            'values_sections_gov',
        ).distinct()

        selected_sub_indicator = [int(x) for x in selected_sub_indicator]
        list_selected_sub = Indicator.objects.filter(id__in=selected_sub_indicator)
        list_selected_sub = list_selected_sub.values(
            'id',
            'ai_id',
            'name',
            'units',
            'target',
            'measurement_type',
            'cumulative_values',
            'values_partners_gov',
            'values_partners',
            'values_gov',
            'values',
        )
        months = []
        for i in range(1, 13):
            months.append((i, datetime.date(2008, i, 1).strftime('%B')))

        # if selected_governorate is not None:
        #     for x in governorates:
        #         if x["location_adminlevel_governorate_code"] == selected_governorate:
        #             selected_governorate_name = x["location_adminlevel_governorate"]

        if selected_partner is not None and len(selected_partner) > 0:
            for x in partners:
                if x["partner_id"] == selected_partner:
                    selected_partner_name = x["partner_label"]
        if selected_section is not None and len(selected_section) > 0:
            for x in sections:
                if x["reporting_section"] == selected_section:
                    selected_section_name = x["reporting_section"]
        report_type ='weekly'
        return {
            'month': month,
            'year': today.year,
            'month_name': month_name,
            'month_number': month_number,
            'months': months,
            'database': database,
            'partners': partners,
            'governorates': governorates,
            'sections':sections,
            'indicators': indicators,
            'indicator': indicator,
            'selected_governorate': selected_governorate,
            'selected_governorate_name': selected_governorate_name,
            'selected_section_name': selected_section_name,
            'selected_section': selected_section,
            'selected_indicator': selected_indicator,
            'selected_sub_indicator': selected_sub_indicator,
            'selected_indicator_name': selected_indicator_name,
            'list_selected_sub': list_selected_sub,
            'selected_filters': selected_filters,
            'current_month': datetime.datetime.now().strftime("%B"),
            'reporting_year': str(reporting_year),
            'selected_partner':selected_partner,
            'selected_partner_name':selected_partner_name,
            'partners_list':partners_list,
            'report_type':report_type

        }


class ReportMapView(TemplateView):
    template_name = 'activityinfo/report_map.html'

    def get_context_data(self, **kwargs):
        from internos.etools.models import PCA
        from internos.activityinfo.utils import load_reporting_map

        now = datetime.now()
        selected_partner = self.request.GET.get('partner', 0)
        selected_governorate = self.request.GET.get('governorate', 0)
        selected_caza = self.request.GET.get('caza', 0)
        selected_donor = self.request.GET.get('donor', 0)

        partner_info = {}
        today = datetime.date.today()
        first = today.replace(day=1)
        last_month = first - datetime.timedelta(days=1)
        month_number = last_month.strftime("%m")
        month = int(last_month.strftime("%m"))
        month_name = last_month.strftime("%B")

        month_number = '12'
        month = 12
        month_name = 'December'

        ai_id = int(self.request.GET.get('ai_id', 0))

        database = Database.objects.get(ai_id=ai_id)

        report = ActivityReport.objects.filter(database=database)
        if database.is_funded_by_unicef:
            report = report.filter(funded_by__contains='UNICEF')

        rows = load_reporting_map(ai_id, partner=selected_partner, governorate=selected_governorate,
                                  caza=selected_caza, donor=selected_donor)

        rows = []
        locations = {}
        ctr = 0
        for item in rows:
            if not item[2] or not item[3]:
                continue
            if item[0] not in locations:
                ctr += 1
                locations[item[0]] = {
                    'location_name': item[1],
                    'location_longitude': item[2],
                    'location_latitude': item[3],
                    'governorate': item[5],
                    'caza': '{}-{}'.format(item[6], item[7]),
                    'cadastral': '{}-{}'.format(item[8], item[9]),
                    'indicators': []
                }

            try:
                cumulative_value = "{:,}".format(round(float(item[12]), 1))
            except Exception:
                cumulative_value = 0

            locations[item[0]]['indicators'].append({
                'indicator_units': item[4].upper(),
                'partner_label': item[10],
                'indicator_name': item[11],
                'cumulative_value': cumulative_value,
            })

        locations = json.dumps(locations.values())

        partners = report.values('partner_label', 'partner_id').distinct()
        governorates = report.values('location_adminlevel_governorate_code',
                                     'location_adminlevel_governorate').distinct()
        cazas = report.values('location_adminlevel_caza_code',
                              'location_adminlevel_caza').distinct()
        indicator_categories = report.values('indicator_category').distinct()
        form_categories = report.values('form_category').distinct()
        months = report.values('month', 'month_name').distinct()

        donors_set = PCA.objects.filter(end__year=now.year, donors__isnull=False, donors__len__gt=0).values('number',
                                                                                                            'donors').distinct()

        donors = {}
        for item in donors_set:
            for donor in item['donors']:
                donors[donor] = donor

        return {
            'selected_partner': selected_partner,
            'selected_governorate': selected_governorate,
            'selected_caza': selected_caza,
            'selected_donor': selected_donor,
            'reports': report.order_by('id'),
            'month': month,
            'year': today.year,
            'month_name': month_name,
            'month_number': month_number,
            'database': database,
            'partners': partners,
            'governorates': governorates,
            'cazas': cazas,
            'donors': donors,
            'locations': locations,
            'indicator_categories': indicator_categories,
            'form_categories': form_categories,
            'months': months,
            'locations_count': ctr
        }


class ReportPartnerSectorView(TemplateView):
    template_name = 'activityinfo/report_partner_sector.html'

    def get_context_data(self, **kwargs):
        partner_info = {}
        today = datetime.date.today()
        first = today.replace(day=1)
        last_month = first - datetime.timedelta(days=1)
        month_number = last_month.strftime("%m")
        month = int(last_month.strftime("%m"))
        month_name = last_month.strftime("%B")

        # month_number = '12'
        # month = 12
        # month_name = 'December'

        selected_indicator = int(self.request.GET.get('indicator_id', 0))
        selected_governorate = self.request.GET.get('governorate', 0)

        ai_id = int(self.request.GET.get('ai_id', 0))

        database = Database.objects.get(ai_id=ai_id)
        indicator = Indicator.objects.get(id=selected_indicator)
        indicator = {
            'id': indicator.id,
            'ai_id': indicator.ai_id,
            'name': indicator.name,
            'explication': indicator.explication,
            'awp_code': indicator.awp_code,
            'measurement_type': indicator.measurement_type,
            'units': indicator.units,
            'target_sector': indicator.target_sector,
            'status_color_sector': indicator.status_color_sector,
            'status_sector': indicator.status_sector,
            'cumulative_values_sector': indicator.cumulative_values_sector,
            'values_partners_sites_sector': indicator.values_partners_sites_sector,
            'values_partners_sector': indicator.values_partners_sector,
            'values_sites_sector': indicator.values_sites_sector,
            'values_sector': indicator.values_sector,
        }

        # report = ActivityReport.objects.filter(database=database)

        partners = get_partners_list(database)
        governorates = get_governorates_list(database)
        cadastrals = get_cadastrals_list(database)

        # partners = report.values('partner_label', 'partner_id').distinct()
        # governorates = report.values('location_adminlevel_governorate_code',
        #                              'location_adminlevel_governorate').distinct()
        # cadastrals = report.values('location_adminlevel_cadastral_area_code',
        #                            'location_adminlevel_cadastral_area').distinct()

        indicators = Indicator.objects.filter(activity__database=database).exclude(is_section=True).order_by('sequence')

        indicators = indicators.values(
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
            'target_sector',
            'status_color_sector',
            'status_sector',
            'cumulative_values_sector',
            'values_partners_sites_sector',
            'values_partners_sector',
            'values_sites_sector',
            'values_sector',
        ).distinct()

        months = []
        for i in range(1, 13):
            months.append((i, datetime.date(2008, i, 1).strftime('%B')))

        return {
            # 'reports': report.order_by('id'),
            'month': month,
            'year': today.year,
            'month_name': month_name,
            'month_number': month_number,
            'months': months,
            'database': database,
            'partners': partners,
            'governorates': governorates,
            'cadastrals': cadastrals,
            'indicators': indicators,
            'indicator': indicator,
            'selected_governorate': selected_governorate,
            'selected_indicator': selected_indicator,
            'selected_partner': 0,
        }


class ReportMapSectorView(TemplateView):
    template_name = 'activityinfo/report_map_sector.html'

    def get_context_data(self, **kwargs):
        from django.db import connection
        from internos.activityinfo.utils import load_reporting_map

        now = datetime.now()
        cursor = connection.cursor()
        selected_filter = False
        partner = None
        rows = []
        selected_partner = self.request.GET.get('partner', 0)
        selected_governorate = self.request.GET.get('governorate', 0)
        selected_caza = self.request.GET.get('caza', 0)

        partner_info = {}
        today = datetime.date.today()
        first = today.replace(day=1)
        last_month = first - datetime.timedelta(days=1)
        month_number = last_month.strftime("%m")
        month = int(last_month.strftime("%m"))
        month_name = last_month.strftime("%B")

        # month_number = '12'
        # month = 12
        # month_name = 'December'

        ai_id = int(self.request.GET.get('ai_id', 0))

        database = Database.objects.get(ai_id=ai_id)

        report = ActivityReport.objects.filter(database=database)

        rows = load_reporting_map(ai_id, partner=selected_partner, governorate=selected_governorate,
                                  caza=selected_caza)

        locations = {}
        ctr = 0
        for item in rows:
            if not item[2] or not item[3]:
                continue
            if item[0] not in locations:
                ctr += 1
                locations[item[0]] = {
                    'location_name': item[1],
                    'location_longitude': item[2],
                    'location_latitude': item[3],
                    'governorate': item[5],
                    'caza': '{}-{}'.format(item[6], item[7]),
                    'cadastral': '{}-{}'.format(item[8], item[9]),
                    'indicators': []
                }

            try:
                cumulative_value = "{:,}".format(round(float(item[12]), 1))
            except Exception:
                cumulative_value = 0

            locations[item[0]]['indicators'].append({
                'indicator_units': item[4].upper(),
                'partner_label': item[10],
                'indicator_name': item[11],
                'cumulative_value': cumulative_value,
            })

        locations = json.dumps(locations.values())

        if selected_partner:
            try:
                partner = Partner.objects.get(number=selected_partner)
                if partner.partner_etools:
                    partner_info = partner.detailed_info
            except Exception as ex:
                print(ex)
                pass

        partners = report.values('partner_label', 'partner_id').distinct()
        governorates = report.values('location_adminlevel_governorate_code',
                                     'location_adminlevel_governorate').distinct()
        cazas = report.values('location_adminlevel_caza_code',
                              'location_adminlevel_caza').distinct()

        return {
            'selected_partner': selected_partner,
            'selected_governorate': selected_governorate,
            'selected_caza': selected_caza,
            'reports': report.order_by('id'),
            'month': month,
            'year': today.year,
            'month_name': month_name,
            'month_number': month_number,
            'database': database,
            'partners': partners,
            'governorates': governorates,
            'cazas': cazas,
            'partner_info': partner_info,
            'partner': partner,
            'selected_filter': selected_filter,
            'locations': locations,
            'locations_count': ctr
        }


class ReportDisabilityView(TemplateView):
    template_name = 'activityinfo/report_disability.html'

    def get_context_data(self, **kwargs):
        from internos.activityinfo.templatetags.util_tags import get_indicator_tag_value
        selected_filter = False
        selected_partners = self.request.GET.getlist('partners', [])
        selected_governorates = self.request.GET.getlist('governorates', [])
        selected_months = self.request.GET.getlist('months',[])
        current_year = date.today().year
        current_month = date.today().month
        today = datetime.date.today()
        first = today.replace(day=1)
        last_month = first - datetime.timedelta(days=1)
        month_number = last_month.strftime("%m")
        month = int(last_month.strftime("%m"))
        month_name = last_month.strftime("%B")
        ai_id = int(self.request.GET.get('ai_id', 0))
        database = Database.objects.get(ai_id=ai_id)
        reporting_year = database.reporting_year.year
        months = []

        if selected_partners or selected_governorates or selected_months:
            selected_filter = True
            partners = get_partners_list(database, govs=selected_governorates,months=selected_months)
            governorates = get_governorates_list(database,partners=selected_partners,months=selected_months)

            if selected_months is not None and len(selected_months) > 0:
                for mon in selected_months:
                    months.append((mon, calendar.month_name[int(mon)]))
            else:
                months = get_months_list(database, selected_partners, selected_governorates)
        else:
            partners = get_partners_list(database)
            governorates = get_governorates_list(database)
            if int(reporting_year) == current_year:

                for i in range(1, current_month):
                    months.append((i, datetime.date(2008, i, 1).strftime('%B')))
            else:
                for i in range(1, 13):
                    months.append((i, datetime.date(2008, i, 1).strftime('%B')))

        tags_disability = Indicator.objects.filter(activity__database__id__exact=database.id,
                                                   tag_disability__isnull=False).exclude(is_sector=True) \
            .values('tag_disability_id', 'tag_disability__name', 'tag_disability__label').distinct().order_by(
            'tag_disability__sequence')

        master_indicators = Indicator.objects.filter(activity__database=database).exclude(is_sector=True).order_by(
            'sequence')
        if database.mapped_db:
            master_indicators = master_indicators.filter(Q(master_indicator=True) | Q(individual_indicator=True))
        support_disabilities = master_indicators.filter(support_disability=True)

        support_disabilities = support_disabilities.values(
            'id',
            'ai_id',
            'name',
            'measurement_type',
            'units',
            'values_tags',
            'cumulative_values',
            'values_partners_gov',
            'values_partners',
            'values_gov',
            'values',
        ).distinct()

        for item in support_disabilities:
            item['cumulative'] = get_indicator_cumulative_months(item, selected_months,
                                                                          selected_partners, selected_governorates,
                                                                          )
        return {
            'selected_partners': selected_partners,
            'selected_governorates': selected_governorates,
            'selected_months':selected_months,
            'month': month,
            'reporting_year':reporting_year,
            'month_name': month_name,
            'month_number': month_number,
            'months': months,
            'database': database,
            'partners': partners,
            'governorates': governorates,
            'master_indicators': support_disabilities,
            'selected_filter': selected_filter,
            'tags_disability': tags_disability,


        }


class ReportDisabilityCrisisView(TemplateView):
    template_name = 'activityinfo/report_crisis_disability.html'

    def get_context_data(self, **kwargs):
        from internos.activityinfo.templatetags.util_tags import get_indicator_tag_value
        selected_filter = False
        selected_partners = self.request.GET.getlist('partners', [])
        selected_governorates = self.request.GET.getlist('governorates', [])
        selected_sections = self.request.GET.getlist('sections', [])
        selected_months = self.request.GET.getlist('months', [])

        today = datetime.date.today()
        first = today.replace(day=1)
        last_month = first - datetime.timedelta(days=1)
        month_number = last_month.strftime("%m")
        month = int(last_month.strftime("%m"))
        month_name = last_month.strftime("%B")
        current_month = date.today().month
        ai_id = int(self.request.GET.get('ai_id', 0))

        database = Database.objects.get(ai_id=ai_id)
        months = []
        if selected_partners or selected_governorates or selected_months or selected_sections:
            selected_filter = True
            partners = get_partners_list(database,selected_sections,selected_governorates,selected_months)
            governorates = get_governorates_list(database,selected_sections,selected_partners,selected_months)
            sections = get_reporting_sections_list(database,selected_partners,selected_governorates,selected_months)
            if selected_months is not None and len(selected_months) > 0:
                for mon in selected_months:
                    months.append((mon, calendar.month_name[int(mon)]))
            else:
                months = get_months_list(database, selected_partners, selected_governorates, selected_sections)
        else:
            partners = get_partners_list(database)
            governorates = get_governorates_list(database)
            sections = get_reporting_sections_list(database)

            for i in range(1, current_month + 1):
                months.append((i, calendar.month_name[i]))

        tags_disability = Indicator.objects.filter(activity__database__id__exact=database.id,
                                                   tag_disability__isnull=False).exclude(is_sector=True) \
            .values('tag_disability_id', 'tag_disability__name', 'tag_disability__label').distinct().order_by(
            'tag_disability__sequence')

        master_indicators = Indicator.objects.filter(activity__database=database).exclude(is_sector=True).order_by(
            'sequence')

        if database.mapped_db:
            master_indicators = master_indicators.filter(Q(master_indicator=True) | Q(individual_indicator=True))
        support_disabilities = master_indicators.filter(support_disability=True)
        support_disabilities = support_disabilities.values(
            'id',
            'ai_id',
            'name',
            'measurement_type',
            'units',
            'values_weekly',
            'values_tags_weekly',
            'values_sections',
            'values_sections_partners',
            'values_sections_gov',
            'values_sections_partners_gov',
            'values_gov_weekly',
            'values_partners_weekly',
            'values_partners_gov_weekly',
            'values_cumulative_weekly',
        ).distinct()
        for item in support_disabilities:
            item['cumulative'] =  get_indicator_cumulative_months_sections(item, selected_months,
                                                                          selected_partners, selected_governorates,
                                                                          selected_sections)
        report_type ='weekly'
        return {
            'selected_partners': selected_partners,
            'selected_governorates': selected_governorates,
            'selected_sections': selected_sections,
            'selected_months':selected_months,
            'month': month,
            'reporting_year': database.reporting_year.year,
            'month_name': month_name,
            'month_number': month_number,
            'months': months,
            'database': database,
            'partners': partners,
            'governorates': governorates,
            'sections':sections,
            'master_indicators': support_disabilities,
            'selected_filter': selected_filter,
            'tags_disability': tags_disability,
            'report_type':report_type
        }


class ReportSectorView(TemplateView):
    template_name = 'activityinfo/report_sector.html'

    def get_context_data(self, **kwargs):
        selected_filter = False
        display_live = False
        selected_partner = self.request.GET.get('partner', 0)
        selected_partners = self.request.GET.getlist('partners', [])
        selected_cadastral = self.request.GET.getlist('cadastral', [])
        selected_months = self.request.GET.getlist('s_months', [])

        partner_info = {}
        current_year = date.today().year
        current_month = date.today().month
        today = datetime.date.today()
        first = today.replace(day=1)
        last_month = first - datetime.timedelta(days=1)
        month_number = last_month.strftime("%m")
        month = int(last_month.strftime("%m"))
        month_name = last_month.strftime("%B")

        # month_number = '12'
        # month = 12
        # month_name = 'December'

        ai_id = int(self.request.GET.get('ai_id', 0))

        database = Database.objects.get(ai_id=ai_id)
        reporting_year = database.reporting_year.name
        report = ActivityReport.objects.filter(database_id=database.ai_id)

        if selected_partner:
            try:
                partner = Partner.objects.get(number=selected_partner)
                if partner.partner_etools:
                    partner_info = partner.detailed_info
            except Exception as ex:
                print(ex)
                pass

        if selected_partners or selected_cadastral or selected_months:
            selected_filter = True

        if selected_partners == [] and selected_cadastral == [] and selected_months == []:
            selected_filter = False

        partners = report.values('partner_label', 'partner_id').distinct()
        cadastrals = report.values('location_adminlevel_cadastral_area_code',
                                   'location_adminlevel_cadastral_area').distinct()
        s_months = []
        if int(reporting_year) == current_year:
            for i in range(1, current_month):
                s_months.append((i, datetime.date(2008, i, 1).strftime('%B')))
        else:
            for i in range(1, 13):
                s_months.append((i, datetime.date(2008, i, 1).strftime('%B')))

        master_indicators = Indicator.objects.filter(activity__database=database).exclude(is_section=True).order_by(
            'sequence')
        if database.mapped_db:
            master_indicators = master_indicators.filter(Q(master_indicator=True) | Q(individual_indicator=True))

        master_indicators = master_indicators.values(
            'id',
            'ai_id',
            'name',
            'master_indicator',
            'master_indicator_sub',
            'master_indicator_sub_sub',
            'individual_indicator',
            'explication',
            'awp_sector_code',
            'measurement_type',
            'units',
            'target',
            'target_sector',
            'status_color',
            'status_color_sector',
            'status',
            'status_sector',
            'cumulative_values_sector',
            'values_partners_sites_sector',
            'values_partners_sector',
            'values_sites_sector',
            'values_sector',

        ).distinct()

        months = []
        if selected_months is not None and len(selected_months) > 0:
            for mon in selected_months:
                months.append((mon, datetime.date(2008, int(mon), 1).strftime('%B')))
        else:
            if int(reporting_year) == current_year:
                display_live = True
                if current_month == 1:
                    months.append((1, datetime.date(2008, 1, 1).strftime('%B')))
                if current_month == 2:
                    for i in range(1, 3):
                        months.append((i, datetime.date(2008, i, 1).strftime('%B')))
                if current_month > 2:
                    for i in range(current_month - 2, current_month + 1):
                        months.append((i, datetime.date(2008, i, 1).strftime('%B')))
            else:
                display_live = False
                for i in range(1, 13):
                    months.append((i, datetime.date(2008, i, 1).strftime('%B')))

        return {
            'selected_partners': selected_partners,
            'selected_cadastral': selected_cadastral,
            'selected_months': selected_months,
            'reports': report.order_by('id'),
            'month': month,
            'year': today.year,
            'month_name': month_name,
            'month_number': month_number,
            'months': months,
            'database': database,
            'partners': partners,
            's_months': s_months,
            'cadastrals': cadastrals,
            'master_indicators': master_indicators,
            'partner_info': partner_info,
            'selected_filter': selected_filter,
            'reporting_year': str(reporting_year),
            'display_live': display_live

        }


class ReportTagView(TemplateView):
    template_name = 'activityinfo/report_tags.html'

    def get_context_data(self, **kwargs):
        from internos.activityinfo.templatetags.util_tags import get_indicator_tag_value

        selected_filter = False
        current_year = date.today().year
        current_month = date.today().month

        selected_partners = self.request.GET.getlist('partners', [])
        selected_months = self.request.GET.getlist('months', [])
        selected_governorates = self.request.GET.getlist('governorates', [])

        today = datetime.date.today()
        first = today.replace(day=1)
        last_month = first - datetime.timedelta(days=1)
        month_number = last_month.strftime("%m")
        month = int(last_month.strftime("%m"))
        month_name = last_month.strftime("%B")

        ai_id = int(self.request.GET.get('ai_id', 0))
        database = Database.objects.get(ai_id=ai_id)
        reporting_year = database.reporting_year.year
        report = ActivityReport.objects.filter(database_id=database.ai_id)

        if database.is_funded_by_unicef:
            report = report.filter(funded_by__contains='UNICEF')
        months = []
        if selected_partners or selected_governorates or selected_months:
            selected_filter = True
            partners = get_partners_list(database, govs=selected_governorates, months=selected_months)
            governorates = get_governorates_list(database, partners=selected_partners, months=selected_months)

            if selected_months is not None and len(selected_months) > 0:
                for mon in selected_months:
                    months.append((mon, calendar.month_name[int(mon)]))
            else:
                months = get_months_list(database, selected_partners, selected_governorates)
        else:
            partners = get_partners_list(database)
            governorates = get_governorates_list(database)
            if int(reporting_year) == current_year:

                for i in range(1, current_month):
                    months.append((i, datetime.date(2008, i, 1).strftime('%B')))
            else:
                for i in range(1, 13):
                    months.append((i, datetime.date(2008, i, 1).strftime('%B')))

        # if selected_partners or selected_governorates or selected_months :
        #     selected_filter = True
        #
        # partners = get_partners_list(database)
        # governorates = get_governorates_list(database)

        tags = IndicatorTag.objects.all().order_by('sequence')

        # if selected_partners or selected_governorates or selected_months:
        #     selected_filter = True


        # if int(reporting_year) == current_year:
        #     for i in range(1, current_month):
        #         months.append((i, datetime.date(2008, i, 1).strftime('%B')))
        # else:
        #     for i in range(1, 13):
        #         months.append((i, datetime.date(2008, i, 1).strftime('%B')))

        all_indicators = Indicator.objects.filter(activity__database=database).exclude(is_sector=True).order_by(
            'sequence')

        tags_gender = all_indicators.filter(tag_gender__isnull=False).exclude(is_sector=True).values(
            'tag_gender__name', 'tag_gender__label').distinct().order_by('tag_gender__sequence')

        tags_gender_number = len(tags_gender)

        tags_nationality = all_indicators.filter(tag_nationality__isnull=False).values(
            'tag_nationality__name', 'tag_nationality__label').distinct().order_by('tag_nationality__sequence')

        tags_nationality_number = len(tags_nationality)

        tags_age = all_indicators.filter(tag_age__isnull=False).values('tag_age__name', 'tag_age__label').distinct()\
            .order_by('tag_age__sequence')
        tags_age_number = len(tags_age)

        tags_disability = all_indicators.filter(tag_disability__isnull=False).values(
            'tag_disability__name', 'tag_disability__label').distinct().order_by('tag_disability__sequence')

        tags_disability_number = len(tags_disability)

        if database.mapped_db:
            master_indicators = all_indicators.filter(Q(master_indicator=True) | Q(individual_indicator=True))

        master_indicators = master_indicators.values(
            'id',
            'ai_id',
            'name',
            'master_indicator',
            'master_indicator_sub',
            'individual_indicator',
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
            'values_tags',
            'is_cumulative',
            'highest_values'
        ).distinct()

        for master_ind in master_indicators:
            if master_ind['is_cumulative']:
                master_ind['cumulative'] = get_indicator_cumulative_months(master_ind, selected_months,
                                                                           selected_partners,
                                                                           selected_governorates,
                                                                           )
            else:
                master_ind['cumulative'] = get_indicator_highest_value(master_ind, selected_months,
                                                                       selected_partners,
                                                                       selected_governorates,
                                                                       )
            master_ind['achieved'] = str(
                calculate_achievement_new(master_ind['target'], master_ind['cumulative'])) + '%'

            sub_indicators = get_sub_master_indicators_data(master_ind['id'], all_indicators)
            master_ind['sub_list'] = sub_indicators
            master_ind['sub_list_filtered'] = sub_indicators
            for sub_ind in sub_indicators:
                if sub_ind['master_indicator']:
                    sub_ind['cumulative'] = 0
                    continue
                else:
                    if master_ind['is_cumulative']:
                        sub_ind['cumulative'] = get_indicator_cumulative_months(sub_ind, selected_months,
                                                                                selected_partners,
                                                                                selected_governorates,
                                                                                )
                    else:
                        sub_ind['cumulative'] = get_indicator_highest_value(sub_ind, selected_months,
                                                                            selected_partners,
                                                                            selected_governorates,
                                                                            )
                    if sub_ind['master_indicator_sub']:
                        sub_ind['achieved'] = str(
                            calculate_achievement_new(sub_ind['target'], sub_ind['cumulative'])) + '%'

        filtered_list = []
        if selected_filter:
            for master_ind in master_indicators:
                if not (master_ind['cumulative'] == '0' or master_ind['cumulative'] == 0):
                    filtered_list.append(master_ind)
                    master_ind['sub_list_filtered'] = []
                    for sub_indicator in master_ind['sub_list']:
                        sub_indicator['sub_list_filtered'] = []
                        if not (sub_indicator['cumulative'] == '0' or sub_indicator['cumulative'] == 0):
                            master_ind['sub_list_filtered'].append(sub_indicator)
                else:
                    for sub_indicator in master_ind['sub_list']:
                        if not (sub_indicator['cumulative'] == '0' or sub_indicator['cumulative'] == 0):
                            filtered_list.append(sub_indicator)
        else:
            filtered_list = master_indicators

        # gender_calculation = {}
        # nationality_calculation = {}
        # age_calculation = {}
        # disability_calculation = {}
        # for item in filtered_list:
        #     for tag in tags_gender:
        #         if tag['tag_gender__label'] not in gender_calculation:
        #             gender_calculation[tag['tag_gender__label']] = 0
        #         value = get_indicator_tag_value(item, tag['tag_gender__name'])
        #         gender_calculation[tag['tag_gender__label']] += float(value)
        #
        #     for tag in tags_nationality:
        #         if tag['tag_nationality__label'] not in nationality_calculation:
        #             nationality_calculation[tag['tag_nationality__label']] = 0
        #         value = get_indicator_tag_value(item, tag['tag_nationality__name'])
        #         nationality_calculation[tag['tag_nationality__label']] += float(value)
        #
        #     for tag in tags_disability:
        #         if tag['tag_disability__label'] not in disability_calculation:
        #             disability_calculation[tag['tag_disability__label']] = 0
        #         value = get_indicator_tag_value(item, tag['tag_disability__name'])
        #         disability_calculation[tag['tag_disability__label']] += float(value)
        #
        #     for tag in tags_age:
        #         if tag['tag_age__name'] not in age_calculation:
        #             age_calculation[tag['tag_age__name']] = 0
        #         value = get_indicator_tag_value(item, tag['tag_age__name'])
        #         age_calculation[tag['tag_age__name']] += float(value)
        #
        # gender_values = []
        # for key, value in gender_calculation.items():
        #     gender_values.append({"label": key, "value": value})
        #
        # nationality_values = []
        # for key, value in nationality_calculation.items():
        #     nationality_values.append({"label": key, "value": value})
        #
        # disability_values = []
        # for key, value in disability_calculation.items():
        #     disability_values.append({"label": key, "value": value})
        #
        # age_values = []
        # for key, value in age_calculation.items():
        #     age_values.append({"label": key, "value": value})

        # months = []
        # for i in range(1, 13):
        #     months.append((i, datetime.date(2008, i, 1).strftime('%B')))

        return {

            'selected_partners': selected_partners,
            'selected_governorates': selected_governorates,
            'selected_months': selected_months,
            'reports': report.order_by('id'),
            'month': month,
            'year': today.year,
            'month_name': month_name,
            'month_number': month_number,
            # 'months': months,
            'database': database,
            'partners': partners,
            'governorates': governorates,
            'months':months,
            'master_indicators': filtered_list,
            'selected_filter': selected_filter,
            'tags': tags,
            'tags_gender': tags_gender,
            'tags_gender_number': tags_gender_number,
            'tags_nationality': tags_nationality,
            'tags_nationality_number': tags_nationality_number,
            'tags_age_number': tags_age_number,
            'tags_age': tags_age,
            'tags_disability_number': tags_disability_number,
            'tags_disability': tags_disability,
            # 'gender_values': json.dumps(gender_values),
            # 'nationality_values': json.dumps(nationality_values),
            # 'disability_values': json.dumps(disability_values),
            # 'age_values': json.dumps(age_values),
            # 'gender_keys': json.dumps(gender_calculation.keys()),
            # 'nationality_keys': json.dumps(nationality_calculation.keys()),
            # 'disability_keys': json.dumps(disability_calculation.keys()),
            # 'age_keys': json.dumps(age_calculation.keys()),
            'reporting_year': str(reporting_year),
            'current_month_name': datetime.datetime.now().strftime("%B")
        }


class ReportCrisisTags(TemplateView):
    template_name = 'activityinfo/report_crisis_tags.html'

    def get_context_data(self, **kwargs):
        from internos.activityinfo.templatetags.util_tags import get_indicator_tag_value

        selected_filter = False
        current_year = date.today().year
        current_month = date.today().month

        selected_partners = self.request.GET.getlist('partners', [])
        selected_months = self.request.GET.getlist('months', [])
        selected_governorates = self.request.GET.getlist('governorates', [])
        selected_sections = self.request.GET.getlist('sections', [])

        today = datetime.date.today()
        first = today.replace(day=1)
        last_month = first - datetime.timedelta(days=1)
        month_number = last_month.strftime("%m")
        month = int(last_month.strftime("%m"))
        month_name = last_month.strftime("%B")

        ai_id = int(self.request.GET.get('ai_id', 0))
        database = Database.objects.get(ai_id=ai_id)
        reporting_year = database.reporting_year.year

        months = []
        if selected_partners or selected_governorates or selected_months or selected_sections:
            selected_filter = True
            partners = get_partners_list(database,selected_sections,selected_governorates,selected_months)
            governorates = get_governorates_list(database,selected_sections,selected_partners,selected_months)
            sections = get_reporting_sections_list(database,selected_partners,selected_governorates,selected_months)
            if selected_months is not None and len(selected_months) > 0:
                for mon in selected_months:
                    months.append((mon, calendar.month_name[int(mon)]))
            else:
                months = get_months_list(database, selected_partners, selected_governorates, selected_sections)
        else:
            partners = get_partners_list(database)
            governorates = get_governorates_list(database)
            sections = get_reporting_sections_list(database)

            for i in range(1, current_month + 1):
                months.append((i, calendar.month_name[i]))

        tags = IndicatorTag.objects.all().order_by('sequence')

        db_indicators = Indicator.objects.filter(activity__database=database).exclude(type='quality') \
            .order_by('sequence')

        imported_indicators = Indicator.objects.filter(activity__database__support_covid=True).exclude(type='quality')
        mixed_indicators = db_indicators | imported_indicators

        tags_gender = mixed_indicators.filter(tag_gender__isnull=False).exclude(is_sector=True).values(
            'tag_gender__name', 'tag_gender__label').distinct().order_by('tag_gender__sequence')

        tags_gender_number = len(tags_gender)

        tags_nationality = mixed_indicators.filter( tag_nationality__isnull=False).exclude(is_sector=True).values(
            'tag_nationality__name', 'tag_nationality__label').distinct().order_by('tag_nationality__sequence')

        tags_nationality_number = len(tags_nationality)

        tags_age = mixed_indicators.filter(tag_age__isnull=False).exclude(is_sector=True).values(
                        'tag_age__name', 'tag_age__label').distinct().order_by('tag_age__sequence')
        tags_age_number = len(tags_age)

        tags_disability = mixed_indicators.filter(tag_disability__isnull=False).exclude(is_sector=True).values(
            'tag_disability__name', 'tag_disability__label').distinct().order_by('tag_disability__sequence')

        tags_disability_number = len(tags_disability)

        master_indicators = db_indicators.filter(activity__database=database).exclude(is_sector=True).order_by(
            'sequence')
        if database.mapped_db:
            master_indicators = master_indicators.filter(Q(master_indicator=True) | Q(individual_indicator=True))

        master_indicators = master_indicators.values(
            'id',
            'ai_id',
            'name',
            'master_indicator',
            'master_indicator_sub',
            'master_indicator_sub_sub',
            'individual_indicator',
            'awp_code',
            'measurement_type',
            'units',
            'values_tags',
            'values_tags_weekly',
            'values_sections',
            'values_sections_partners',
            'values_sections_gov',
            'values_sections_partners_gov',
            'values_weekly',
            'values_gov_weekly',
            'values_partners_weekly',
            'values_partners_gov_weekly',
            'values_cumulative_weekly',
            'activity',
            'activity__database__label'
        ).distinct()

        for master_ind in master_indicators:
            master_ind['cumulative'] = get_indicator_cumulative_months_sections(master_ind, selected_months,
                                                                          selected_partners, selected_governorates,
                                                                          selected_sections)

            sub_indicators = get_sub_master_indicators_crisis_data(master_ind['id'],mixed_indicators)
            master_ind['sub_list'] = sub_indicators
            master_ind['sub_list_filtered'] = sub_indicators
            for ind in sub_indicators:
                if ind['master_indicator'] and not ind['is_imported']:
                    ind['cumulative'] = 0
                    continue
                if ind['is_imported']:
                    if len(selected_sections) > 0:
                        for section in selected_sections:
                            if '/' in section:
                                var1 = section.split('/')[0]
                                var2 = section.split('/')[1]
                                if var1 in ind['activity__database__label'] or var2 in ind['activity__database__label']:
                                    ind['cumulative'] = get_indicator_cumulative_months_sections(ind, selected_months,
                                                                                             selected_partners,
                                                                                             selected_governorates)
                            elif ind['activity__database__label'] == section:
                                ind['cumulative'] = get_indicator_cumulative_months_sections(ind, selected_months,
                                         selected_partners, selected_governorates)
                            else:
                                ind['cumulative'] = 0
                    else:
                        ind['cumulative'] = get_indicator_cumulative_months_sections(ind, selected_months,
                                                                                     selected_partners,
                                                                                     selected_governorates,
                                                                                     )
                else:
                    ind['cumulative'] = get_indicator_cumulative_months_sections(ind, selected_months,
                                                                                 selected_partners,
                                                                                 selected_governorates,
                                                                                 selected_sections)

        filtered_list=[]
        if selected_filter:
            for master_ind in master_indicators:
                if not (master_ind['cumulative'] == '0' or master_ind['cumulative'] == 0):
                    filtered_list.append(master_ind)
                    master_ind['sub_list_filtered']=[]
                    for sub_indicator in master_ind['sub_list']:
                        sub_indicator['sub_list_filtered'] = []
                        if not (sub_indicator['cumulative'] == '0' or sub_indicator['cumulative'] == 0):
                            master_ind['sub_list_filtered'].append(sub_indicator)

                else:
                    for sub_indicator in master_ind['sub_list']:
                        if not (sub_indicator['cumulative'] == '0' or sub_indicator['cumulative'] == 0):
                            filtered_list.append(sub_indicator)

                        else:
                            continue

        else:
            filtered_list = master_indicators

        covid_indicators = imported_indicators.filter(support_COVID=True).filter(master_indicator=True).exclude(is_imported=True)

        covid_indicators = covid_indicators.values(
            'id',
            'ai_id',
            'name',
            'master_indicator',
            'master_indicator_sub',
            'master_indicator_sub_sub',
            'individual_indicator',
            'awp_code',
            'measurement_type',
            'units',
            'values_tags',
            'values_tags_weekly',
            'values',
            'values_gov',
            'values_partners',
            'values_partners_gov',
            'cumulative_values',
            'activity'
        ).distinct()
        start_month = 4  # used to get cumulative values starting this month for covid reporting

        filtered_covid_indicators = []

        if len(selected_sections) > 0:
            for section in selected_sections:
                if '/' in section:
                    section = section.split('/')
                    filtered =list(covid_indicators.filter(Q(activity__database__label__contains=section[0]) | Q(activity__database__label__contains=section[1])))
                    for item in filtered:
                        filtered_covid_indicators.append(item)
                else:
                    filtered = list(covid_indicators.filter(activity__database__label__contains=section))
                    for item in filtered:
                        filtered_covid_indicators.append(item)
        else:
            filtered_covid_indicators = covid_indicators

        for master_ind in filtered_covid_indicators:
            master_ind['cumulative'] = get_indicator_cumulative_months(master_ind, selected_months,
                                                                       selected_partners,
                                                                       selected_governorates,
                                                                       start_month)
            sub_indicators = get_sub_master_indicators_data(master_ind['id'], imported_indicators)
            master_ind['sub_list'] = sub_indicators
            master_ind['sub_list_filtered'] = sub_indicators
            for ind in sub_indicators:
                ind['cumulative'] = get_indicator_cumulative_months(ind, selected_months,
                                                                    selected_partners,
                                                                    selected_governorates,
                                                                    start_month
                                                                    )

        covid_filtered_list = []
        if selected_filter:
            for master_ind in filtered_covid_indicators:
                if not (master_ind['cumulative'] == '0' or master_ind['cumulative'] == 0):
                    covid_filtered_list.append(master_ind)
                    master_ind['sub_list_filtered'] = []
                    for sub_indicator in master_ind['sub_list']:
                        sub_indicator['sub_list_filtered'] = []
                        if not (sub_indicator['cumulative'] == '0' or sub_indicator['cumulative'] == 0):
                            master_ind['sub_list_filtered'].append(sub_indicator)
                else:
                    for sub_indicator in master_ind['sub_list']:
                        if not (sub_indicator['cumulative'] == '0' or sub_indicator['cumulative'] == 0):
                            covid_filtered_list.append(sub_indicator)
                        else:
                            continue

        else:
            covid_filtered_list = filtered_covid_indicators

        start_month = 4
        report_type='weekly'
        # months = []
        # for i in range(1, 13):
        #     months.append((i, datetime.date(2008, i, 1).strftime('%B')))

        return {

            'selected_partners': selected_partners,
            'selected_governorates': selected_governorates,
            'selected_months': selected_months,
            'selected_sections':selected_sections,
            'month': month,
            'year': today.year,
            'month_name': month_name,
            'month_number': month_number,
            'months': months,
            'database': database,
            'partners': partners,
            'governorates': governorates,
            'master_indicators': filtered_list,
            'selected_filter': selected_filter,
            'tags': tags,
            'tags_gender': tags_gender,
            'tags_gender_number': tags_gender_number,
            'tags_nationality': tags_nationality,
            'tags_nationality_number': tags_nationality_number,
            'tags_age_number': tags_age_number,
            'tags_age': tags_age,
             'tags_disability_number': tags_disability_number,
            'tags_disability': tags_disability,
            # 'gender_values': json.dumps(gender_values),
            # 'nationality_values': json.dumps(nationality_values),
            # 'disability_values': json.dumps(disability_values),
            # 'age_values': json.dumps(age_values),
            # 'gender_keys': json.dumps(gender_calculation.keys()),
            # 'nationality_keys': json.dumps(nationality_calculation.keys()),
            # 'disability_keys': json.dumps(disability_calculation.keys()),
            # 'age_keys': json.dumps(age_calculation.keys()),
            'reporting_year': str(reporting_year),
            'current_month_name': datetime.datetime.now().strftime("%B"),
            'sections':sections,
            'covid_indicators':covid_filtered_list,
            'start_month':start_month,
            'report_type':report_type
        }


class ReportCrisisVisualView(TemplateView):
    template_name = 'activityinfo/report_crisis_visual.html'

    def get_context_data(self, **kwargs):

        return {

        }


class LiveReportView(TemplateView):
    template_name = 'activityinfo/live.html'

    def get_context_data(self, **kwargs):
        selected_filter = False
        selected_partners = self.request.GET.getlist('partners', [])
        selected_governorates = self.request.GET.getlist('governorates', [])

        partner_info = {}
        today = datetime.date.today()
        day_number = today.strftime("%d")
        month_number = today.strftime("%m")
        month = int(today.strftime("%m"))-1
        month_name = calendar.month_name[month]

        ai_id = int(self.request.GET.get('ai_id', 0))

        database = Database.objects.get(ai_id=ai_id)
        reporting_year = database.reporting_year

        report = LiveActivityReport.objects.filter(database_id=database.ai_id)
        if database.is_funded_by_unicef:
            report = report.filter(funded_by__contains='UNICEF')

        if selected_partners or selected_governorates :
            selected_filter = True
            partners = get_partners_list(database, govs= selected_governorates, report_type= 'live')
            governorates = get_governorates_list(database, partners=selected_partners, report_type= 'live')

        else:
            partners = get_partners_list(database, report_type='live')
            governorates = get_governorates_list(database, report_type='live')

        all_indicators = Indicator.objects.filter(activity__database=database).order_by('sequence')

        master_indicators = all_indicators.filter(activity__database=database).exclude(is_sector=True).order_by(
            'sequence')
        if database.mapped_db:
            master_indicators = master_indicators.filter(Q(master_indicator=True) | Q(individual_indicator=True))

        master_indicators = master_indicators.values(
            'id',
            'ai_id',
            'name',
            'master_indicator',
            'master_indicator_sub',
            'individual_indicator',
            'awp_code',
            'measurement_type',
            'units',
            'target',
            'status_color',
            'status',
            'cumulative_values_live',
            'values_partners_gov_live',
            'values_partners_live',
            'values_gov_live',
            'values_live',
            'is_cumulative',
            'highest_values_live'
        ).distinct()
        for master_ind in master_indicators:
            if master_ind['is_cumulative']:
                master_ind['cumulative'] = get_indicator_live_cumulative(master_ind, month,
                                                                           selected_partners,
                                                                           selected_governorates,
                                                                           )
            else:
                master_ind['cumulative'] = get_indicator_highest_value_live(master_ind, month,
                                                                       selected_partners,
                                                                       selected_governorates,
                                                                       )
            master_ind['achieved'] = str(
                calculate_achievement_new(master_ind['target'], master_ind['cumulative'])) + '%'

            sub_indicators = get_sub_indicators_live_data(master_ind['id'], all_indicators)
            master_ind['sub_list'] = sub_indicators
            master_ind['sub_list_filtered'] = sub_indicators
            for sub_ind in sub_indicators:
                if sub_ind['master_indicator']:
                    sub_ind['cumulative'] = 0
                    continue
                else:
                    if master_ind['is_cumulative']:
                        sub_ind['cumulative'] = get_indicator_live_cumulative(sub_ind, month,
                                                                                selected_partners,
                                                                                selected_governorates,
                                                                                )
                    else:
                        sub_ind['cumulative'] = get_indicator_highest_value_live(sub_ind, month,
                                                                            selected_partners,
                                                                            selected_governorates,
                                                                            )
                    if sub_ind['master_indicator_sub']:
                        sub_ind['achieved'] = str(
                            calculate_achievement_new(sub_ind['target'], sub_ind['cumulative'])) + '%'

                sub_sub_indicators = get_sub_indicators_live_data(sub_ind['id'], all_indicators)
                sub_ind['sub_list'] = sub_sub_indicators
                sub_ind['sub_list_filtered'] = sub_sub_indicators
                for ind in sub_sub_indicators:
                    if ind['master_indicator']:
                        ind['cumulative'] = 0
                        continue
                    else:
                        if master_ind['is_cumulative']:
                            ind['cumulative'] = get_indicator_live_cumulative(ind, month,
                                                                                selected_partners,
                                                                                selected_governorates,
                                                                                )
                        else:
                            ind['cumulative'] = get_indicator_highest_value_live(ind, month,
                                                                            selected_partners,
                                                                            selected_governorates,
                                                                            )

        filtered_list = []
        if selected_filter:
            for master_ind in master_indicators:
                if not (master_ind['cumulative'] == '0' or master_ind['cumulative'] == 0):
                    filtered_list.append(master_ind)
                    master_ind['sub_list_filtered'] = []
                    for sub_indicator in master_ind['sub_list']:
                        sub_indicator['sub_list_filtered'] = []
                        if not (sub_indicator['cumulative'] == '0' or sub_indicator['cumulative'] == 0):
                            master_ind['sub_list_filtered'].append(sub_indicator)
                        for sub_sub_ind in sub_indicator['sub_list']:
                            if sub_sub_ind['cumulative'] == '0' or sub_sub_ind['cumulative'] == 0:
                                continue
                            else:
                                sub_indicator['sub_list_filtered'].append(sub_sub_ind)
                else:
                    for sub_indicator in master_ind['sub_list']:
                        if not (sub_indicator['cumulative'] == '0' or sub_indicator['cumulative'] == 0):
                            filtered_list.append(sub_indicator)
                            sub_indicator['sub_list_filtered'] = []
                            for sub_sub_ind in sub_indicator['sub_list']:
                                if sub_sub_ind['cumulative'] == '0' or sub_sub_ind['cumulative'] == 0:
                                    continue
                                else:
                                    sub_indicator['sub_list_filtered'].append(sub_sub_ind)
                        else:
                            for sub_sub_ind in sub_indicator['sub_list']:
                                if sub_sub_ind['cumulative'] == '0' or sub_sub_ind['cumulative'] == 0:
                                    continue
                                else:
                                    filtered_list.append(sub_sub_ind)
        else:
            filtered_list = master_indicators

        return {
            'selected_partners': selected_partners,
            'selected_governorates': selected_governorates,
            'reports': report.order_by('id'),
            'month': month,
            'month_name': month_name,
            'month_number': month_number,
            'database': database,
            'partners': partners,
            'governorates': governorates,
            'master_indicators': filtered_list,
            'selected_filter': selected_filter,
            'partner_info': partner_info,
            'day_number': day_number,
            'reporting_year': str(reporting_year)
        }


class HPMView(TemplateView):
    template_name = 'activityinfo/hpm.html'

    def get_context_data(self, **kwargs):

        current_month = date.today().month
        current_year = date.today().year
        is_current_year = True
        title = ""
        table_title=""
        month = int(self.request.GET.get('month', 0))
        type = self.request.GET.get('quarter', "")
        today = datetime.date.today()
        day_number = int(today.strftime("%d"))

        if month == 0:
            if day_number >= 15:
                month = current_month - 1
            else:
                month = current_month - 2

        # year = date.today().year
        # reporting_year = self.request.GET.get('rep_year', year)
        instance = ReportingYear.objects.get(current=True)
        reporting_year = self.request.GET.get('rep_year', instance.year)
        # if not reporting_year:
        #     reporting_year = year

        if type == '1' or type == '2':
            selected_month_name='Quarter ' + type
        else:
            selected_month_name = calendar.month_name[month]

        month_name = calendar.month_name[month]

        if int(reporting_year) != current_year:
            is_current_year = False

        databases = Database.objects.filter(reporting_year__name=reporting_year).exclude(ai_id=10240).order_by('hpm_sequence')

        SGBV_db = [x for x in databases if x.label == 'SGBV']
        if SGBV_db is None:
            SGBV_db_id=0
        else:
            SGBV_db_id = SGBV_db[0].ai_id

        if type == '1':
            title = '{} {}'.format('HPM Table | Data of January-March |', str(reporting_year))
            table_title = ""
        elif  type == '2':
            title = '{} {}'.format('HPM Table | Data of January-June |', str(reporting_year))
            table_title = ""
        elif month == 1 and type == "":
            title = '{} {}'.format('HPM Table | Data of January |', str(reporting_year))
            table_title='{} {} {}'.format('SUMMARY OF PROGRAMME RESULTS | January | ',str(reporting_year),'SITREP-LEBANON')
        else:
            title = '{} {} {} {}'.format('HPM Table | Data of January to ', str(month_name),'|', str(reporting_year))
            table_title='{} {} {} {} {}'.format('SUMMARY OF PROGRAMME RESULTS | January to',  month_name , '|',  reporting_year,'SITREP-LEBANON')

        months = []
        if int(reporting_year) == current_year:
            if current_month == 1:
                months.append((1, datetime.date(2008, 1, 1).strftime('%B')))
            if current_month > 2:
                if day_number >= 15:
                    for i in range(1, current_month):
                        months.append((i, datetime.date(2008, i, 1).strftime('%B')))
                else:
                    for i in range(1, current_month-1):
                        months.append((i, datetime.date(2008, i, 1).strftime('%B')))

        if current_year - 1 == int(reporting_year) and current_month == 1:
            months = []
            is_current_year = True
            for i in range(1, 13):
                months.append((i, datetime.date(2008, i, 1).strftime('%B')))

        # periodic_months=[3,6,9,12]
        # periodic_list=[]
        # for m in periodic_months:
        #     if m < current_month:
        #         periodic_list.append((m,'Quarter: '+ datetime.date(2008, m, 1).strftime('%B')))

        return {
            'ai_databases': databases,
            'month_name': month_name,
            'month': month,
            'months': months,
            'reporting_year': reporting_year,
            'is_current_year': is_current_year,
            'title': title,
            'SGBV_db': SGBV_db_id,
            'table_title':table_title,
            'selected_month':selected_month_name,
            # 'periodic_months':periodic_list,
            'type':type
        }

    def post(self, request, *args, **kwargs):

        indicator_id = self.request.POST.get('indicator', 0)
        comment = self.request.POST.get('comment',"")
        indicator = Indicator.objects.get(id=indicator_id)
        month = self.request.POST.get('month',0)
        if indicator:
            comments_list = indicator.comment
            if comments_list is None:
                comments_list = {}
            if month > 0:
                comments_list[month] = comment
                indicator.comment = comments_list
                indicator.save()
        return HttpResponseRedirect('/activityinfo/HPM/?rep_year=2020&month='+month)


class HPMExportViewSet(ListView):
    model = Indicator
    queryset = Indicator.objects.filter(hpm_indicator=True)

    def get(self, request, *args, **kwargs):
        from .utils import update_hpm_table_docx
        year = date.today().year
        reporting_year = self.request.GET.get('rep_year', year)
        type = self.request.GET.get('type', "")
        if reporting_year is None:
            reporting_year = year
        today = datetime.date.today()
        first = today.replace(day=1)
        currnet_month = first - datetime.timedelta(days=1)
        day_number = int(today.strftime("%d"))
        month = int(self.request.GET.get('month', currnet_month.strftime("%m")))

        # month = int(self.request.GET.get('month', int(today.strftime("%m")) - 1))
        # month = 12
        # if day_number < 15:
        #     month = month - 1

        months = []
        for i in range(1, 13):
            months.append((datetime.date(2008, i, 1).strftime('%B')))

        filename = "HPM Table {} {}.docx".format(months[month-1], reporting_year)
        new_file = update_hpm_table_docx(self.queryset, month, months[month-1], filename,reporting_year,type)

        with open(new_file, 'rb') as fh:
            response = HttpResponse(
                fh.read(),
                content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )
            response['Content-Disposition'] = 'attachment; filename=' + filename
        return response


class ExportViewSet1(ListView):
    model = ActivityReport
    queryset = ActivityReport.objects.all()

    def get(self, request, *args, **kwargs):

        ai_id = self.request.GET.get('ai_id', 0)
        month = int(self.request.GET.get('month', int(datetime.now().strftime("%m")) - 1))
        report_format = self.request.GET.get('format', 0)

        instance = Database.objects.get(ai_id=ai_id)
        report_mapping = getattr(instance, report_format)

        qs = ActivityReport.objects.filter(
            database_id=ai_id,
            start_date__month=month)
        if instance.is_funded_by_unicef:
            qs = qs.filter(funded_by__contains='UNICEF')

        filename = "extraction.csv"

        fields = report_mapping.keys()
        header = report_mapping.values()
        if report_format == 'mapping_extraction3':
            header = fields

        meta = {
            'file': filename,
            # 'file': '/{}/{}'.format('tmp', filename),
            'queryset': qs,
            'fields': fields,
            'header': header
        }
        from internos.backends.gistfile import get_model_as_csv_file_response
        return get_model_as_csv_file_response(meta, content_type='text/csv', filename=filename)


class ExportDataSet(ListView):
    model = ActivityReport
    queryset = ActivityReport.objects.all()

    def get(self, request, *args, **kwargs):

        qs = ActivityReport.objects.filter(
            start_date__year='2020')

        path = os.path.dirname(os.path.abspath(__file__))

        filename = "AI full raw data.csv"
        filename = path + '/AIReports/' + filename
        fields = []
        model_fields = ActivityReport._meta.fields

        for field in model_fields:
            fields.append(field.name)

        meta = {
            'file': filename,
            # 'file': '/{}/{}'.format('tmp', filename),
            'queryset': qs,
            'fields': fields,
            'header': fields
        }

        # from internos.backends.djqscsv import render_to_csv_response
        # return render_to_csv_response(qs, field_header_map=fields, field_order=fields)

        from internos.backends.gistfile import get_model_as_csv_file_response
        return get_model_as_csv_file_response(meta, content_type='text/csv', filename=filename)


class ExportViewSet(ListView):
    model = ActivityReport
    queryset = ActivityReport.objects.none()

    def get(self, request, *args, **kwargs):
        ai_id = self.request.GET.get('ai_id', 0)
        instance = Database.objects.get(ai_id=ai_id)

        today = datetime.date.today()
        first = today.replace(day=1)
        last_month = first - datetime.timedelta(days=1)
        month_name = last_month.strftime("%B")
        path = os.path.dirname(os.path.abspath(__file__))
        if instance.reporting_year.name == '2020':
            path2file = path + '/AIReports/' + str(instance.db_id) + '_ai_data.csv'
        else:
            path2file = path + '/AIReports/' + str(instance.ai_id) + '_ai_data.csv'
        filename = '{}_{}_{}_Raw Data.csv'.format(instance.label, month_name, instance.reporting_year.name)
        with open(path2file, 'r') as f:
            response = HttpResponse(f.read(), content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename=%s;' % filename
        return response


class ReportBBlastView(TemplateView):
    template_name = 'activityinfo/blast.html'

    def get_context_data(self, **kwargs):

        return {
        }


class ReportBlastView(TemplateView):
    template_name = 'activityinfo/report_blast.html'

    def get_context_data(self, **kwargs):

        ai_id = int(self.request.GET.get('ai_id', 0))
        database = Database.objects.get(ai_id=ai_id)
        reporting_year = database.reporting_year.year
        current_month = date.today().month
        all_indicators = Indicator.objects.filter(activity__database=database).exclude(type='quality') \
            .order_by('sequence')
        months = []
        for i in range(1, current_month + 1):
            months.append((i, calendar.month_name[i]))

        return {
            'database': database,
            'reporting_year': str(reporting_year),
            'current_month_name':  datetime.datetime.now().strftime("%B"),
            'months' : months,
            'indicators': all_indicators
        }


def load_sections(request):

    from django.db import connection
    partners = request.GET.getlist('partner_id[]')
    govs = request.GET.getlist('gov_id[]')
    ai_id = request.GET.get('ai_id')
    months = request.GET.getlist('month_id[]')
    report_type= request.GET.get('type')
    database = Database.objects.get(ai_id=ai_id)

    result = {}
    cursor = connection.cursor()
    where_condition = ""
    funded_condition = ""

    if database.is_funded_by_unicef:
        funded_condition = " AND funded_by = 'UNICEF' "

    if partners:
        partners_list = ", ".join("'" + str(n) + "'" for n in partners)
        where_condition += " AND partner_id in (" + partners_list + ")"
    if govs:
        govs_list = ", ".join("'" + str(n) + "'" for n in govs)
        where_condition = " and location_adminlevel_governorate_code in (" + govs_list + ")"
    if months:
        month_list = ", ".join("'" + str(n) + "'" for n in months)
        where_condition += " AND date_part('month', start_date) in (" + month_list + ")"

    query_condition = "{}'{}'".format(" WHERE database_id =", str(ai_id)) + funded_condition + where_condition
    if report_type == 'live':
        cursor.execute(
            "SELECT DISTINCT reporting_section "
            "FROM activityinfo_liveactivityreport " + query_condition)
    else:
        cursor.execute(
            "SELECT DISTINCT reporting_section "
            "FROM activityinfo_activityreport " + query_condition
        )
    rows = cursor.fetchall()

    for row in rows:
        result[row[0]] = {
            'reporting_section': row[0],
        }

    # if partnerId and govId and monthId:
    #
    #     if type =='live':
    #         report = LiveActivityReport.objects.filter(database_id=ai_id, location_adminlevel_governorate_code__in=govId,
    #                                            partner_id__in=partnerId, start_date__month__in=monthId) \
    #             .order_by('location_adminlevel_governorate_code').distinct('location_adminlevel_governorate_code')
    #     else:
    #         report = ActivityReport.objects.filter(database_id=ai_id, location_adminlevel_governorate_code__in=govId,
    #                                                partner_id__in=partnerId, start_date__month__in=monthId) \
    #             .order_by('location_adminlevel_governorate_code','partner_id').distinct('location_adminlevel_governorate_code','partner_id')
    #
    # elif govId and partnerId and len(monthId) == 0:
    #
    #     if type == 'live':
    #         report = LiveActivityReport.objects.filter(database_id=ai_id, location_adminlevel_governorate_code__in=govId,
    #                                            partner_id__in=partnerId) \
    #         .order_by('location_adminlevel_governorate_code').distinct('location_adminlevel_governorate_code',)
    #     else :
    #         report = ActivityReport.objects.filter(database_id=ai_id, location_adminlevel_governorate_code__in=govId,
    #                                                partner_id__in=partnerId)
    #
    # elif partnerId and monthId and (govId is None and len(govId)) == 0:
    #
    #     if type == 'live':
    #         report = LiveActivityReport.objects.filter(database_id=ai_id, start_date__month__in=monthId, partner_id__in=partnerId) \
    #             .order_by('partner_id').distinct('partner_id')
    #     else:
    #         report = ActivityReport.objects.filter(database_id=ai_id, start_date__month__in=monthId,
    #                                                partner_id__in=partnerId)
    #
    # elif govId and monthId and (partnerId is None and len(partnerId)) == 0:
    #
    #     if type == 'live':
    #         report = LiveActivityReport.objects.filter(database_id=ai_id, start_date__month__in=monthId,
    #                                             location_adminlevel_governorate_code__in=govId)\
    #         .order_by('location_adminlevel_governorate_code').distinct('location_adminlevel_governorate_code')
    #     else:
    #         report = ActivityReport.objects.filter(database_id=ai_id, start_date__month__in=monthId,
    #                                                location_adminlevel_governorate_code__in=govId)
    #
    # elif monthId and (govId is None and len(govId)) == 0 and (partnerId is None and len(partnerId)) == 0:
    #
    #     if type == 'live':
    #         report = LiveActivityReport.objects.filter(database_id=ai_id, start_date__month__in=monthId)
    #     else :
    #         report = ActivityReport.objects.filter(database_id=ai_id, start_date__month__in=monthId)
    #
    # elif partnerId and (govId is None and len(govId)) == 0 and (monthId is None and len(monthId)) == 0:
    #
    #     if type == 'live':
    #          report = LiveActivityReport.objects.filter(database_id=ai_id, partner_id__in=partnerId) \
    #              .order_by('partner_id').distinct('partner_id')
    #     else:
    #         report = ActivityReport.objects.filter(database_id=ai_id, partner_id__in=partnerId)
    #
    # elif govId and (partnerId is None and len(partnerId)) == 0 and (monthId is None and len(monthId)) == 0:
    #
    #     if type == 'live':
    #         report = LiveActivityReport.objects.filter(database_id=ai_id,  location_adminlevel_governorate_code__in=govId) \
    #             .order_by('location_adminlevel_governorate_code').distinct('location_adminlevel_governorate_code')
    #     else:
    #         report = ActivityReport.objects.filter(database_id=ai_id, location_adminlevel_governorate_code__in=govId)
    # else:
    #
    #     if type == 'live':
    #          report = LiveActivityReport.objects.filter(database_id=ai_id)
    #     else :
    #         report = ActivityReport.objects.filter(database_id=ai_id)
    #
    # if database.is_funded_by_unicef:
    #     report = report.filter(funded_by__contains='UNICEF')
    #
    # sections = report.values('reporting_section').order_by('reporting_section').distinct('reporting_section')

    return render(request, 'activityinfo/section_dropdown_list_options.html', {'sections': result.values()})


def load_partners(request):
    from django.db import connection

    govId = request.GET.getlist('gov_id[]')
    ai_id = request.GET.get('ai_id')
    monthId = request.GET.getlist('month_id[]')
    sectionId = request.GET.getlist('section_id[]')
    database = Database.objects.get(ai_id=ai_id)
    report_type = request.GET.get('type')

    result = {}
    cursor = connection.cursor()
    where_condition = ""
    funded_condition = ""

    if database.is_funded_by_unicef:
        funded_condition = " AND funded_by = 'UNICEF' "
    if govId:
        govs_list = ", ".join("'" + str(n) + "'" for n in govId)
        where_condition = " and location_adminlevel_governorate_code in (" + govs_list + ")"

    if sectionId:
        section_list = ", ".join("'" + str(n) + "'" for n in sectionId)
        where_condition += " AND reporting_section in (" + section_list + ")"

    if monthId:
        month_list = ", ".join("'" + str(n) + "'" for n in monthId)
        where_condition += " AND date_part('month', start_date) in (" + month_list + ")"

    query_condition = "{}'{}'".format(" WHERE database_id =", str(ai_id)) + funded_condition + where_condition

    if report_type == 'live':
        cursor.execute(
            "SELECT DISTINCT partner_id, partner_label "
            "FROM activityinfo_liveactivityreport "
            + query_condition)
    else:
        cursor.execute(
            "SELECT DISTINCT partner_id, partner_label "
            "FROM activityinfo_activityreport "
            + query_condition)

    rows = cursor.fetchall()

    for row in rows:
        result[row[0]] = {
            'partner_id': row[0],
            'partner_label': row[1]
        }
    # return result.values()
    return render(request, 'activityinfo/partner_dropdown_list_options.html', {'partners':  result.values()})


def load_governorates(request):
    from django.db import connection

    partners = request.GET.getlist('partner_id[]')
    sections = request.GET.getlist('section_id[]')
    months= request.GET.getlist('month_id[]')
    ai_id = request.GET.get('ai_id')
    database = Database.objects.get(ai_id=ai_id)
    report_type = request.GET.get('type')

    result = {}
    cursor = connection.cursor()
    where_condition = ""
    funded_condition = ""

    if database.is_funded_by_unicef:
        funded_condition = " AND funded_by = 'UNICEF' "

    if sections:
        section_list = ", ".join("'" + str(n) + "'" for n in sections)
        where_condition += " AND reporting_section in (" + section_list + ")"
    if partners:
        partners_list = ", ".join("'" + str(n) + "'" for n in partners)
        where_condition += " AND partner_id in (" + partners_list + ")"
    if months:
        month_list = ", ".join("'" + str(n) + "'" for n in months)
        where_condition += " AND date_part('month', start_date) in (" + month_list + ")"

    query_condition = "{}'{}'".format(" WHERE database_id =", str(ai_id)) + funded_condition + where_condition

    if report_type == 'live':
        cursor.execute(
            "SELECT DISTINCT location_adminlevel_governorate_code, location_adminlevel_governorate "
            "FROM activityinfo_liveactivityreport "
            + query_condition)
    else:
        cursor.execute(
            "SELECT DISTINCT location_adminlevel_governorate_code, location_adminlevel_governorate "
            "FROM activityinfo_activityreport "
            + query_condition)

    rows = cursor.fetchall()

    for row in rows:
        result[row[0]] = {
            'location_adminlevel_governorate_code': row[0],
            'location_adminlevel_governorate': row[1]
        }

    # if partnerId and sectionId and monthId:
    #     if type == 'live':
    #          report = ActivityReport.objects.filter(database_id=ai_id, partner_id__in=partnerId,
    #                                            reporting_section__in=sectionId , start_date__month__in=monthId) \
    #                     .order_by('reporting_section').distinct('reporting_section')
    #
    #     else :
    #         report = ActivityReport.objects.filter(database_id=ai_id, partner_id__in=partnerId,
    #                                                reporting_section__in=sectionId, start_date__month__in=monthId)
    # elif partnerId and (sectionId is None or len(sectionId) == 0) and monthId:
    #     if type == 'live':
    #         report = LiveActivityReport.objects.filter(database_id=ai_id, partner_id__in=partnerId, start_date__month__in=monthId)\
    #                 .order_by('partner_id').distinct('partner_id')
    #
    #     else:
    #         report = ActivityReport.objects.filter(database_id=ai_id, partner_id__in=partnerId,
    #                                                start_date__month__in=monthId)
    #
    # elif partnerId and sectionId and len(monthId) == 0 :
    #         if type == 'live':
    #              report = LiveActivityReport.objects.filter(database_id=ai_id , partner_id__in=partnerId,reporting_section__in=sectionId) \
    #                  .order_by('partner_id').distinct('partner_id')
    #         else:
    #             report = ActivityReport.objects.filter(database_id=ai_id, partner_id__in=partnerId,
    #                                                    reporting_section__in=sectionId)
    #
    # elif monthId and sectionId and len(partnerId) == 0:
    #     if type == 'live':
    #         report = LiveActivityReport.objects.filter(database_id=ai_id, start_date__month__in=monthId,
    #                                            reporting_section__in=sectionId) \
    #             .order_by('reporting_section').distinct('reporting_section')
    #     else :
    #         report = ActivityReport.objects.filter(database_id=ai_id, start_date__month__in=monthId,
    #                                                reporting_section__in=sectionId)
    #
    # elif partnerId and (sectionId is None or len(sectionId) == 0) and len(monthId) ==0 :
    #     if type == 'live':
    #         report = LiveActivityReport.objects.filter(database_id=ai_id, partner_id__in=partnerId) \
    #             .order_by('partner_id').distinct('partner_id')
    #     else :
    #         report = ActivityReport.objects.filter(database_id=ai_id, partner_id__in=partnerId)
    #
    # elif sectionId and (partnerId is None or len(partnerId) == 0) and len(monthId) == 0:
    #
    #     if type == 'live':
    #         report = LiveActivityReport.objects.filter(database_id=ai_id, reporting_section__in=sectionId) \
    #             .order_by('reporting_section').distinct('reporting_section')
    #     else :
    #         report = ActivityReport.objects.filter(database_id=ai_id, reporting_section__in=sectionId)
    #
    # elif monthId and (sectionId is None or len(sectionId) == 0) and len(partnerId) == 0:
    #     if type == 'live':
    #         report = LiveActivityReport.objects.filter(database_id=ai_id, start_date__month__in=monthId)
    #     else :
    #         report = ActivityReport.objects.filter(database_id=ai_id, start_date__month__in=monthId)
    # else:
    #     if type == 'live':
    #
    #          report = LiveActivityReport.objects.filter(database_id=ai_id)
    #     else :
    #         report = ActivityReport.objects.filter(database_id=ai_id)
    #
    # if database.is_funded_by_unicef:
    #         report = report.filter(funded_by__contains='UNICEF')
    # governorates = report.values('location_adminlevel_governorate_code',
    #                                                            'location_adminlevel_governorate').distinct()

    return render(request, 'activityinfo/gov_dropdown_list_options.html', {'governorates':  result.values()})


def load_months(request):
    from django.db import connection

    partners = request.GET.getlist('partner_id[]')
    sections = request.GET.getlist('section_id[]')
    govs = request.GET.getlist('gov_id[]')
    ai_id = request.GET.get('ai_id')
    database = Database.objects.get(ai_id=ai_id)
    report_type = request.GET.get('type')
    result = {}
    months = []
    cursor = connection.cursor()
    where_condition = ""
    funded_condition = ""

    if database.is_funded_by_unicef:
        funded_condition = " AND funded_by = 'UNICEF' "

    if partners:
        partners_list = ", ".join("'" + str(n) + "'" for n in partners)
        where_condition += " AND partner_id in (" + partners_list + ")"
    if govs:
        govs_list = ", ".join("'" + str(n) + "'" for n in govs)
        where_condition = " and location_adminlevel_governorate_code in (" + govs_list + ")"
    if sections:
        section_list = ", ".join("'" + str(n) + "'" for n in sections)
        where_condition += " AND reporting_section in (" + section_list + ")"

    query_condition = "{}'{}'".format(" WHERE database_id =", str(ai_id)) + funded_condition + where_condition

    if report_type == 'live':
        cursor.execute(
            "SELECT DISTINCT start_date "
            "FROM activityinfo_liveactivityreport " + query_condition

        )
    else:
        cursor.execute(
            "SELECT DISTINCT start_date "
            "FROM activityinfo_activityreport " + query_condition
        )
    rows = cursor.fetchall()

    for row in rows:
        if row[0] is not None:
            result[row[0]] = {
                'start_date': row[0],
            }
    sorted_list = sorted(result)
    for record in sorted_list:
        if record is not None:
            m = record.month
            if (m, calendar.month_name[m]) not in months:
                months.append((m, calendar.month_name[m]))
    return render(request, 'activityinfo/month_dropdown_list_options.html', {'months': months})


    # return months
    # if partnerId and sectionId and govId:
    #     report = ActivityReport.objects.filter(database_id=ai_id, partner_id__in=partnerId,
    #                                            reporting_section__in=sectionId,location_adminlevel_governorate_code__in=govId)
    #     result_list = report.values('start_date').distinct()
    #
    #     for record in result_list:
    #         if 'start_date' in record and record['start_date'] is not None:
    #             m = record['start_date'].month
    #             if (m, calendar.month_name[m]) not in months:
    #                 months.append((m,calendar.month_name[m]))
    #
    # elif partnerId and sectionId and (govId is None or len(govId) == 0):
    #
    #      report = ActivityReport.objects.filter(database_id=ai_id , partner_id__in=partnerId,reporting_section__in=sectionId)
    #      result_list = report.values('start_date').distinct()
    #
    #      for record in result_list:
    #          if 'start_date' in record and record['start_date'] is not None:
    #              m = record['start_date'].month
    #              if (m, calendar.month_name[m]) not in months:
    #                  months.append((m, calendar.month_name[m]))
    #
    # elif partnerId and govId and (sectionId is None or len(sectionId) == 0):
    #
    #     report = ActivityReport.objects.filter(database_id=ai_id, partner_id__in=partnerId,location_adminlevel_governorate_code__in=govId)
    #     result_list = report.values('start_date').distinct()
    #     for record in result_list:
    #         if 'start_date' in record and record['start_date'] is not None:
    #             m = record['start_date'].month
    #             if (m, calendar.month_name[m]) not in months:
    #                 months.append((m, calendar.month_name[m]))
    #
    # elif sectionId and govId and (partnerId is None or len(partnerId) == 0):
    #
    #     report = ActivityReport.objects.filter(database_id=ai_id, reporting_section__in=sectionId,
    #                                            location_adminlevel_governorate_code__in=govId)
    #     result_list = report.values('start_date').distinct()
    #     for record in result_list:
    #         if 'start_date' in record and record['start_date'] is not None:
    #             m = record['start_date'].month
    #             if (m, calendar.month_name[m]) not in months:
    #                 months.append((m, calendar.month_name[m]))
    #
    # elif partnerId and (sectionId is None or len(sectionId) == 0) and (govId is None or len(govId) == 0):
    #     report = ActivityReport.objects.filter(database_id=ai_id, partner_id__in=partnerId)
    #     result_list = report.values('start_date').distinct()
    #     for record in result_list:
    #         if 'start_date' in record and record['start_date'] is not None:
    #             m = record['start_date'].month
    #             if (m, calendar.month_name[m]) not in months:
    #                 months.append((m, calendar.month_name[m]))
    #
    # elif govId and (sectionId is None or len(sectionId) == 0) and (partnerId is None or len(partnerId) == 0):
    #
    #     report = ActivityReport.objects.filter(database_id=ai_id,location_adminlevel_governorate_code__in=govId)
    #     result_list = report.values('start_date').distinct()
    #
    #     for record in result_list:
    #         if 'start_date' in record and record['start_date'] is not None:
    #             m = record['start_date'].month
    #             if (m, calendar.month_name[m]) not in months:
    #                 months.append((m, calendar.month_name[m]))
    # elif sectionId and (govId is None or len(govId) == 0) and (partnerId is None or len(partnerId) == 0):
    #
    #     report = ActivityReport.objects.filter(database_id=ai_id, reporting_section__in=sectionId)
    #     result_list = report.values('start_date').distinct()
    #
    #     for record in result_list:
    #         if 'start_date' in record and record['start_date'] is not None:
    #             m = record['start_date'].month
    #             if (m, calendar.month_name[m]) not in months:
    #                 months.append((m, calendar.month_name[m]))
    # else:
    #
    #     for i in range(1, 13):
    #         months.append((i, calendar.month_abbr[i]))

class ActivityAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated():
            return Activity.objects.none()

        qs = Activity.objects.filter(database__reporting_year__year=datetime.datetime.now().year)

        if self.q:
            qs = Activity.objects.filter(name__istartswith=self.q)

        return qs


class IndicatorsListVisualView(TemplateView):
    template_name = 'activityinfo/indicators_list_visual.html'

    def get_context_data(self, **kwargs):
        pillar = self.request.GET.get('pillar', 0)
        reporting_level = self.request.GET.get('reporting_level', 0)
        focus_name = self.request.GET.get('focus_name', 0)
        color = self.request.GET.get('color', 0)

        indicators = Indicator.objects.filter(activity__database__ai_id='202020',
                                              master_indicator=True).order_by('sequence')

        if pillar:
            indicators = indicators.filter(category=pillar)
        if reporting_level:
            indicators = indicators.filter(reporting_level__contains=reporting_level)
        if focus_name:
            indicators = indicators.filter(tag_focus__name=focus_name)

        indicators = indicators.values(
            'id',
            'ai_id',
            'name',
            'master_indicator',
            'master_indicator_sub',
            'master_indicator_sub_sub',
            'individual_indicator',
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
            'is_cumulative',
            'support_COVID',
            'category',
            'tag_focus__name',
            'values_tags',
            'reporting_level',
        ).distinct().order_by('sequence')

        return {
            'count': indicators.count(),
            'indicators': indicators,
            'color': color,
            'filter': 'level3-filter',
            'display_tags': True
        }


class IndicatorsSubListVisualView(TemplateView):
    template_name = 'activityinfo/indicators_list_visual.html'

    def get_context_data(self, **kwargs):
        parent_id = self.request.GET.get('parent_id', 0)
        color = self.request.GET.get('color', 0)

        indicators = Indicator.objects.filter(activity__database__ai_id='202020',
                                              master_indicator=False)

        if parent_id:
            indicators = indicators.filter(sub_indicators=int(parent_id))

        indicators = indicators.values(
            'id',
            'ai_id',
            'name',
            'master_indicator',
            'master_indicator_sub',
            'master_indicator_sub_sub',
            'individual_indicator',
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
            'is_cumulative',
            'support_COVID',
            'category',
            'tag_focus__name',
            'values_tags',
            'reporting_level',
        ).distinct().order_by('sequence')

        return {
            'count': indicators.count(),
            'indicators': indicators,
            'color': color,
            'filter': 'level4-filter',
            'display_tags': False
        }

