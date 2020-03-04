from __future__ import absolute_import, unicode_literals

import os
import json
import datetime
import calendar
from django.db.models import Q, Sum
from django.views.generic import ListView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse

from internos.backends.djqscsv import render_to_csv_response
from braces.views import GroupRequiredMixin, SuperuserRequiredMixin
from .models import ActivityReport, LiveActivityReport, Database, Indicator, Partner, IndicatorTag, ReportingYear
from internos.users.models import Section
from datetime import date


class IndexView(TemplateView):
    template_name = 'activityinfo/index.html'

    def get_context_data(self, **kwargs):
        year = date.today().year
        reporting_year = self.request.GET.get('rep_year', year)

        if reporting_year is None: reporting_year == year

        databases = Database.objects.filter(reporting_year__name=reporting_year).exclude(ai_id=10240).order_by('label')
        db_year = databases[0].reporting_year

        return {
            'ai_databases': databases,
            'reporting_year':reporting_year
        }


class DashboardView(TemplateView):
    template_name = 'activityinfo/dashboard.html'

    def get_context_data(self, **kwargs):
        month = int(self.request.GET.get('month', int(datetime.datetime.now().strftime("%m")) - 1))
        month_name = self.request.GET.get('month', datetime.datetime.now().strftime("%B"))
        ai_id = int(self.request.GET.get('ai_id', 0))
        from datetime import date
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
        selected_partner = self.request.GET.get('partner', 0)
        selected_partners = self.request.GET.getlist('partners', [])
        selected_partner_name = self.request.GET.get('partner_name', 'All Partners')
        selected_governorate = self.request.GET.get('governorate', 0)
        selected_governorates = self.request.GET.getlist('governorates', [])
        selected_governorate_name = self.request.GET.get('governorate_name', 'All Governorates')

        current_year = date.today().year
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
        reporting_year = database.reporting_year

        report = ActivityReport.objects.filter(database_id=database.ai_id)

        if database.is_funded_by_unicef:
            report = report.filter(funded_by__contains='UNICEF')

        if selected_partner:
            try:
                partner = Partner.objects.get(number=selected_partner)
                if partner.partner_etools:
                    partner_info = partner.detailed_info
            except Exception as ex:
                print(ex)
                pass

        # if selected_partner or selected_governorate:
        if selected_partners or selected_governorates:
            selected_filter = True

        # if selected_partner == '0' and selected_governorate == '0':
        # if selected_partners == [] and selected_governorate == '0':
        #     selected_filter = False

        partners = report.values('partner_label', 'partner_id').distinct()
        governorates = report.values('location_adminlevel_governorate_code',
                                     'location_adminlevel_governorate').distinct()

        master_indicators = Indicator.objects.filter(activity__database=database).exclude(is_sector=True).order_by(
            'sequence')
        if database.mapped_db:
            master_indicators1 = master_indicators.filter(master_indicator=True)
            master_indicators2 = master_indicators.filter(
                sub_indicators__isnull=True, individual_indicator=True
            )
            master_indicators = master_indicators1 | master_indicators2
        none_ai_indicators = Indicator.objects.filter(activity__none_ai_database=database).exclude(is_sector=True)

        master_indicators = master_indicators.values(
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

        none_ai_indicators = none_ai_indicators.values(
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

        months = []

        if reporting_year == current_year:
            for i in range(1, 4):
                months.append((i, datetime.date(2008, i, 1).strftime('%B')))
        else:
            for i in range(1, 13):
                months.append((i, datetime.date(2008, i, 1).strftime('%B')))
        return {
            # 'selected_partner': selected_partner,
            'selected_partners': selected_partners,
            'selected_partner_name': selected_partner_name,
            # 'selected_governorate': selected_governorate,
            'selected_governorates': selected_governorates,
            'selected_governorate_name': selected_governorate_name,
            'reports': report.order_by('id'),
            'month': month,
            'year': today.year,
            'month_name': month_name,
            'month_number': month_number,
            'months': months,
            'database': database,
            'partners': partners,
            'governorates': governorates,
            'master_indicators': master_indicators,
            'partner_info': partner_info,
            'selected_filter': selected_filter,
            'none_ai_indicators': none_ai_indicators,
            'reporting_year': str(reporting_year)
        }


class ReportPartnerView(TemplateView):
    template_name = 'activityinfo/report_partner.html'

    def get_context_data(self, **kwargs):

        from internos.activityinfo.utils import load_reporting_map

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

        selected_indicator = int(self.request.GET.get('indicator_id', 0))
        selected_governorate = self.request.GET.get('governorate', 0)
        selected_governorate_name = self.request.GET.get('governorate_name', 'All Governorates')

        ai_id = int(self.request.GET.get('ai_id', 0))

        database = Database.objects.get(ai_id=ai_id)
        reporting_year = database.reporting_year

        indicator = Indicator.objects.get(id=selected_indicator)
        selected_indicator_name = indicator.name
        indicator = {
            'id': indicator.id,
            'ai_id': indicator.ai_id,
            'name': indicator.name,
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
            'reporting_year': str(reporting_year)
        }

        report = ActivityReport.objects.filter(database_id=database.ai_id)
        if database.is_funded_by_unicef:
            report = report.filter(funded_by__contains='UNICEF')

        partners = report.values('partner_label', 'partner_id').distinct()
        governorates = report.values('location_adminlevel_governorate_code',
                                     'location_adminlevel_governorate').distinct()

        indicators = Indicator.objects.filter(activity__database=database).exclude(is_sector=True).order_by('sequence')

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

        months = []
        for i in range(1, 13):
            months.append((i, datetime.date(2008, i, 1).strftime('%B')))

        report = ActivityReport.objects.filter(database=database)
        if database.is_funded_by_unicef:
            report = report.filter(funded_by__contains='UNICEF')

        rows = load_reporting_map(ai_id, indicator=selected_indicator)

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

        if selected_governorate is not None:
            for x in governorates:
                if x["location_adminlevel_governorate_code"] == selected_governorate:
                    selected_governorate_name = x["location_adminlevel_governorate"]

        return {
            'reports': report.order_by('id'),
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
            'selected_indicator_name': selected_indicator_name,
            'locations': locations,
        }


class ReportMapView(TemplateView):
    template_name = 'activityinfo/report_map.html'

    def get_context_data(self, **kwargs):
        from django.db import connection
        from internos.etools.models import PCA
        from internos.activityinfo.templatetags.util_tags import number_format
        from internos.activityinfo.utils import load_reporting_map

        now = datetime.datetime.now()
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

        month_number = '12'
        month = 12
        month_name = 'December'

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

        report = ActivityReport.objects.filter(database=database)

        partners = report.values('partner_label', 'partner_id').distinct()
        governorates = report.values('location_adminlevel_governorate_code',
                                     'location_adminlevel_governorate').distinct()
        cadastrals = report.values('location_adminlevel_cadastral_area_code',
                                   'location_adminlevel_cadastral_area').distinct()

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
            'reports': report.order_by('id'),
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

        now = datetime.datetime.now()
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

        month_number = '12'
        month = 12
        month_name = 'December'

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
        selected_partner = self.request.GET.get('partner', 0)
        selected_partners = self.request.GET.getlist('partners', [])
        selected_partner_name = self.request.GET.get('partner_name', 'All Partners')
        selected_governorate = self.request.GET.get('governorate', 0)
        selected_governorates = self.request.GET.get('governorates', 0)
        selected_governorate_name = self.request.GET.get('governorate_name', 'All Governorates')

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

        tags_disability = Indicator.objects.filter(activity__database__id__exact=database.id,
                                                   tag_disability__isnull=False).exclude(is_sector=True) \
            .values('tag_disability_id', 'tag_disability__name', 'tag_disability__label').distinct().order_by(
            'tag_disability__sequence')

        tags_gender = Indicator.objects.filter(activity__database__id__exact=database.id,
                                               tag_gender__isnull=False).exclude(is_sector=True) \
            .values('tag_gender__name', 'tag_gender__label').distinct().order_by('tag_gender__sequence')

        partners = report.values('partner_label', 'partner_id').distinct()
        governorates = report.values('location_adminlevel_governorate_code',
                                     'location_adminlevel_governorate').distinct()

        master_indicators = Indicator.objects.filter(activity__database=database).exclude(is_sector=True).order_by(
            'sequence')
        if database.mapped_db:
            master_indicators = master_indicators.filter(Q(master_indicator=True) | Q(individual_indicator=True))

        master_indicators = master_indicators.values(
            'id',
            'ai_id',
            'name',
            'target',
            'values',
            'values_tags',
            'cumulative_values',
        ).distinct()

        support_disabilities = master_indicators.filter(support_disability=True)

        disability_calculation = {}
        for item in master_indicators:
            for tag in tags_disability:
                if tag['tag_disability__label'] not in disability_calculation:
                    disability_calculation[tag['tag_disability__label']] = 0
                value = get_indicator_tag_value(item, tag['tag_disability__name'])
                disability_calculation[tag['tag_disability__label']] += float(value)

        indicators = Indicator.objects.filter(activity__database=database).values(
            'tag_gender',
            'tag_age',
            'tag_disability',
            'tag_nationality',
            'values',
            'values_partners',
            'values_gov',
        )

        disability_per_partner = {}
        disability_partners = {}
        partners1 = report.filter(ai_indicator__tag_disability__isnull=False).values('partner_label',
                                                                                     'partner_id').distinct()
        for partner in partners1:
            if partner['partner_id'] not in disability_partners:
                disability_partners[partner['partner_id']] = partner['partner_label']
            partner_indicators = indicators.filter(report_indicators__partner_id=partner['partner_id'])

            for tag in tags_disability:
                p_value = 0
                if tag['tag_disability__label'] not in disability_per_partner:
                    disability_per_partner[tag['tag_disability__label']] = []
                tag_indicators = partner_indicators.filter(tag_disability_id=tag['tag_disability_id'])

                for indicator in tag_indicators:
                    values_partners = indicator['values_partners']
                    for key, value in values_partners.items():
                        keys = key.split('-')
                        if partner['partner_id'] == keys[1]:
                            p_value += int(value)

                disability_per_partner[tag['tag_disability__label']].append({
                    'name': partner['partner_label'],
                    'y': p_value,
                    'x': partner['partner_label'],
                    'type': tag['tag_disability__label']
                })

        disability_per_gov = {}
        disability_govs = {}
        govs1 = report.filter(ai_indicator__tag_disability__isnull=False).values('location_adminlevel_governorate_code',
                                                                                 'location_adminlevel_governorate').distinct()
        for gov in govs1:
            if gov['location_adminlevel_governorate_code'] not in disability_govs:
                disability_govs[gov['location_adminlevel_governorate_code']] = gov['location_adminlevel_governorate']
            gov_indicators = indicators.filter(
                report_indicators__location_adminlevel_governorate_code=gov['location_adminlevel_governorate_code'])

            for tag in tags_disability:
                p_value = 0
                if tag['tag_disability__label'] not in disability_per_gov:
                    disability_per_gov[tag['tag_disability__label']] = []
                tag_indicators = gov_indicators.filter(tag_disability_id=tag['tag_disability_id'])

                for indicator in tag_indicators:
                    values_gov = indicator['values_gov']
                    for key, value in values_gov.items():
                        keys = key.split('-')
                        if gov['location_adminlevel_governorate_code'] == keys[1]:
                            p_value += int(value)

                disability_per_gov[tag['tag_disability__label']].append({
                    'name': gov['location_adminlevel_governorate'],
                    'y': p_value,
                    'x': gov['location_adminlevel_governorate'],
                    'type': tag['tag_disability__label']
                })

        disability_values = []
        for key, value in disability_calculation.items():
            disability_values.append({"label": key, "value": value})

        months = []
        for i in range(1, 13):
            months.append((i, datetime.date(2008, i, 1).strftime('%B')))

        return {
            'selected_partner': selected_partner,
            'selected_partners': selected_partners,
            'selected_partner_name': selected_partner_name,
            'selected_governorate': selected_governorate,
            'selected_governorates': selected_governorates,
            'selected_governorate_name': selected_governorate_name,
            'reports': report.order_by('id'),
            'month': month,
            'year': today.year,
            'month_name': month_name,
            'month_number': month_number,
            'months': months,
            'database': database,
            'partners': partners,
            'governorates': governorates,
            'master_indicators': support_disabilities,
            'partner_info': partner_info,
            'selected_filter': selected_filter,
            'tags_disability': tags_disability,
            'disability_values': json.dumps(disability_values),
            'disability_keys': json.dumps(disability_calculation.keys()),
            'disability_per_partner': json.dumps(disability_per_partner.values()),
            'disability_partners': json.dumps(disability_partners.values()),
            'disability_per_gov': json.dumps(disability_per_gov.values()),
            'disability_govs': json.dumps(disability_govs.values()),

        }


class ReportSectorView(TemplateView):
    template_name = 'activityinfo/report_sector.html'

    def get_context_data(self, **kwargs):
        selected_filter = False
        selected_partner = self.request.GET.get('partner', 0)
        selected_partners = self.request.GET.getlist('partners', [])
        selected_governorate = self.request.GET.get('governorate', 0)
        selected_cadastral = self.request.GET.get('cadastral', 0)
        selected_governorates = self.request.GET.get('governorates', 0)

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

        if ai_id:
            database = Database.objects.get(ai_id=ai_id)
        else:
            try:
                section = self.request.user.section
                database = Database.objects.get(section=section, reporting_year__current=True)
            except Exception:
                database = Database.objects.filter(reporting_year__current=True).first()

        report = ActivityReport.objects.filter(database=database)

        if selected_partner:
            try:
                partner = Partner.objects.get(number=selected_partner)
                if partner.partner_etools:
                    partner_info = partner.detailed_info
            except Exception as ex:
                print(ex)
                pass

        if selected_partners or selected_cadastral:
            selected_filter = True

        if selected_partners == [] and selected_cadastral == '0':
            selected_filter = False

        partners = report.values('partner_label', 'partner_id').distinct()
        governorates = report.values('location_adminlevel_governorate_code',
                                     'location_adminlevel_governorate').distinct()
        cadastrals = report.values('location_adminlevel_cadastral_area_code',
                                   'location_adminlevel_cadastral_area').distinct()

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
            'awp_code',
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
        for i in range(1, 13):
            months.append((i, datetime.date(2008, i, 1).strftime('%B')))

        return {
            'selected_partner': selected_partner,
            'selected_partners': selected_partners,
            'selected_governorate': selected_governorate,
            'selected_cadastral': selected_cadastral,
            'selected_governorates': selected_governorates,
            'reports': report.order_by('id'),
            'month': month,
            'year': today.year,
            'month_name': month_name,
            'month_number': month_number,
            'months': months,
            'database': database,
            'partners': partners,
            'governorates': governorates,
            'cadastrals': cadastrals,
            'master_indicators': master_indicators,
            'partner_info': partner_info,
            'selected_filter': selected_filter,

        }


class ReportTagView(TemplateView):
    template_name = 'activityinfo/report_tags.html'

    def get_context_data(self, **kwargs):
        from internos.activityinfo.templatetags.util_tags import get_indicator_tag_value
        selected_filter = False
        selected_partner = self.request.GET.get('partner', 0)
        selected_partners = self.request.GET.getlist('partners', [])
        selected_partner_name = self.request.GET.get('partner_name', 'All Partners')
        selected_governorate = self.request.GET.get('governorate', 0)
        selected_governorates = self.request.GET.get('governorates', 0)
        selected_governorate_name = self.request.GET.get('governorate_name', 'All Governorates')

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
        tags = IndicatorTag.objects.all().order_by('sequence')

        if ai_id:
            database = Database.objects.get(ai_id=ai_id)
        else:
            try:
                section = self.request.user.section
                database = Database.objects.get(section=section, reporting_year__current=True)
            except Exception:
                database = Database.objects.filter(reporting_year__current=True).first()

        reporting_year = database.reporting_year
        report = ActivityReport.objects.filter(database=database)
        if database.is_funded_by_unicef:
            report = report.filter(funded_by__contains='UNICEF')

        tags_gender = Indicator.objects.filter(activity__database__id__exact=database.id,
                                               tag_gender__isnull=False).exclude(is_sector=True).values(
            'tag_gender__name', 'tag_gender__label').distinct().order_by('tag_gender__sequence')
        tags_nationality = Indicator.objects.filter(activity__database__id__exact=database.id,
                                                    tag_nationality__isnull=False).exclude(is_sector=True).values(
            'tag_nationality__name', 'tag_nationality__label').distinct().order_by('tag_nationality__sequence')
        tags_age = Indicator.objects.filter(activity__database__id__exact=database.id,
                                            tag_age__isnull=False).exclude(is_sector=True).values('tag_age__name',
                                                                                                  'tag_age__label').distinct().order_by(
            'tag_age__sequence')
        tags_disability = Indicator.objects.filter(activity__database__id__exact=database.id,
                                                   tag_disability__isnull=False).exclude(is_sector=True).values(
            'tag_disability__name', 'tag_disability__label').distinct().order_by('tag_disability__sequence')

        if selected_partner:
            try:
                partner = Partner.objects.get(number=selected_partner)
                if partner.partner_etools:
                    partner_info = partner.detailed_info
            except Exception as ex:
                print(ex)
                pass

        # if selected_partner or selected_governorate:
        if selected_partners or selected_governorate:
            selected_filter = True

        # if selected_partner == '0' and selected_governorate == '0':
        if selected_partners == [] and selected_governorate == '0':
            selected_filter = False

        partners = report.values('partner_label', 'partner_id').distinct()
        governorates = report.values('location_adminlevel_governorate_code',
                                     'location_adminlevel_governorate').distinct()

        master_indicators = Indicator.objects.filter(activity__database=database).exclude(is_sector=True).order_by(
            'sequence')
        if database.mapped_db:
            master_indicators = master_indicators.filter(Q(master_indicator=True) | Q(individual_indicator=True))

        none_ai_indicators = Indicator.objects.filter(activity__none_ai_database=database).exclude(is_sector=True)

        master_indicators = master_indicators.values(
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
            'values_tags',
        ).distinct()

        gender_calculation = {}
        nationality_calculation = {}
        age_calculation = {}
        disability_calculation = {}
        for item in master_indicators:
            for tag in tags_gender:
                if tag['tag_gender__label'] not in gender_calculation:
                    gender_calculation[tag['tag_gender__label']] = 0
                value = get_indicator_tag_value(item, tag['tag_gender__name'])
                gender_calculation[tag['tag_gender__label']] += float(value)

            for tag in tags_nationality:
                if tag['tag_nationality__label'] not in nationality_calculation:
                    nationality_calculation[tag['tag_nationality__label']] = 0
                value = get_indicator_tag_value(item, tag['tag_nationality__name'])
                nationality_calculation[tag['tag_nationality__label']] += float(value)

            for tag in tags_disability:
                if tag['tag_disability__label'] not in disability_calculation:
                    disability_calculation[tag['tag_disability__label']] = 0
                value = get_indicator_tag_value(item, tag['tag_disability__name'])
                disability_calculation[tag['tag_disability__label']] += float(value)

            for tag in tags_age:
                if tag['tag_age__name'] not in age_calculation:
                    age_calculation[tag['tag_age__name']] = 0
                value = get_indicator_tag_value(item, tag['tag_age__name'])
                age_calculation[tag['tag_age__name']] += float(value)

        gender_values = []
        for key, value in gender_calculation.items():
            gender_values.append({"label": key, "value": value})

        nationality_values = []
        for key, value in nationality_calculation.items():
            nationality_values.append({"label": key, "value": value})

        disability_values = []
        for key, value in disability_calculation.items():
            disability_values.append({"label": key, "value": value})

        age_values = []
        for key, value in age_calculation.items():
            age_values.append({"label": key, "value": value})

        months = []
        for i in range(1, 13):
            months.append((i, datetime.date(2008, i, 1).strftime('%B')))

        return {
            'selected_partner': selected_partner,
            'selected_partners': selected_partners,
            'selected_partner_name': selected_partner_name,
            'selected_governorate': selected_governorate,
            'selected_governorates': selected_governorates,
            'selected_governorate_name': selected_governorate_name,
            'reports': report.order_by('id'),
            'month': month,
            'year': today.year,
            'month_name': month_name,
            'month_number': month_number,
            'months': months,
            'database': database,
            'partners': partners,
            'governorates': governorates,
            'master_indicators': master_indicators,
            'partner_info': partner_info,
            'selected_filter': selected_filter,
            'none_ai_indicators': none_ai_indicators,
            'tags': tags,
            'tags_gender': tags_gender,
            'tags_nationality': tags_nationality,
            'tags_age': tags_age,
            'tags_disability': tags_disability,
            'gender_values': json.dumps(gender_values),
            'nationality_values': json.dumps(nationality_values),
            'disability_values': json.dumps(disability_values),
            'age_values': json.dumps(age_values),
            'gender_keys': json.dumps(gender_calculation.keys()),
            'nationality_keys': json.dumps(nationality_calculation.keys()),
            'disability_keys': json.dumps(disability_calculation.keys()),
            'age_keys': json.dumps(age_calculation.keys()),
            'reporting_year':str(reporting_year)
        }


class LiveReportView(TemplateView):
    template_name = 'activityinfo/live.html'

    def get_context_data(self, **kwargs):
        selected_filter = False
        selected_partner = self.request.GET.get('partner', 0)
        selected_partners = self.request.GET.getlist('partners', [])
        selected_partner_name = self.request.GET.get('partner_name', 'All Partners')
        selected_governorate = self.request.GET.get('governorate', 0)
        selected_governorates = self.request.GET.getlist('governorates', [])
        selected_governorate_name = self.request.GET.get('governorate_name', 'All Governorates')

        partner_info = {}
        today = datetime.date.today()
        day_number = today.strftime("%d")
        month_number = today.strftime("%m")
        month = int(today.strftime("%m"))
        month_name = today.strftime("%B")

        ai_id = int(self.request.GET.get('ai_id', 0))

        database = Database.objects.get(ai_id=ai_id)
        reporting_year= database.reporting_year
        report = LiveActivityReport.objects.filter(database=database)
        if database.is_funded_by_unicef:
            report = report.filter(funded_by__contains='UNICEF')

        if selected_partner:
            try:
                partner = Partner.objects.get(number=selected_partner)
                if partner.partner_etools:
                    partner_info = partner.detailed_info
            except Exception as ex:
                # print(ex)
                pass
        if selected_partners or selected_governorates:
            selected_filter = True

        partners = report.values('partner_label', 'partner_id').distinct('partner_id')

        governorates = report.values('location_adminlevel_governorate_code',
                                     'location_adminlevel_governorate').distinct('location_adminlevel_governorate_code')

        master_indicators = Indicator.objects.filter(activity__database=database).exclude(is_sector=True).order_by('sequence')
        if database.mapped_db:
            master_indicators = master_indicators.filter(Q(master_indicator=True) | Q(individual_indicator=True))

        months = []
        for i in range(1, 13):
            months.append((i, datetime.date(2008, i, 1).strftime('%B')))

        master_indicators = master_indicators.values(
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
            'cumulative_values_live',
            'values_partners_gov_live',
            'values_partners_live',
            'values_gov_live',
            'values_live',
        ).distinct()

        return {
            'selected_partners': selected_partners,
            'selected_partner_name': selected_partner_name,
            'selected_governorates': selected_governorates,
            'selected_governorate_name': selected_governorate_name,
            'reports': report.order_by('id'),
            'month': month,
            'month_name': month_name,
            'month_number': month_number,
            'database': database,
            'partners': partners.distinct(),
            'governorates': governorates.distinct(),
            'master_indicators': master_indicators,
            'selected_filter': selected_filter,
            'partner_info': partner_info,
            'day_number': day_number,
            'months': months,
            'reporting_year':str(reporting_year)
        }


class HPMView(TemplateView):
    template_name = 'activityinfo/hpm.html'

    def get_context_data(self, **kwargs):
        today = datetime.date.today()
        # first = today.replace(day=1)
        # last_month = first - datetime.timedelta(days=1)
        # day_number = int(today.strftime("%d"))
        # month = int(self.request.GET.get('month', last_month.strftime("%m")))
        month = int(self.request.GET.get('month', int(today.strftime("%m")) - 1))
        month = 12
        # if day_number < 15:
        #     month = month - 1

        month_name = calendar.month_name[month]
        month_name = 'December'

        months = []
        for i in range(1, 13):
            months.append({
                'month': i,
                'month_name': (datetime.date(2008, i, 1).strftime('%B'))
            })

        return {
            'month_name': month_name,
            'month': month,
            'months': months,
        }


class HPMExportViewSet(ListView):
    model = Indicator
    queryset = Indicator.objects.filter(hpm_indicator=True)

    def get(self, request, *args, **kwargs):
        from .utils import update_hpm_table_docx

        today = datetime.date.today()
        # first = today.replace(day=1)
        # last_month = first - datetime.timedelta(days=1)
        day_number = int(today.strftime("%d"))
        # month = int(self.request.GET.get('month', last_month.strftime("%m")))
        month = int(self.request.GET.get('month', int(today.strftime("%m")) - 1))
        month = 12
        # if day_number < 15:
        #     month = month - 1

        months = []
        for i in range(1, 13):
            months.append((datetime.date(2008, i, 1).strftime('%B')))

        # filename = "HPM Table {} 2019.docx".format(months[month])
        filename = "HPM Table December 2019.docx"

        # new_file = update_hpm_table_docx(self.queryset, month, months[month], filename)
        new_file = update_hpm_table_docx(self.queryset, month, 'December', filename)

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
        month = int(self.request.GET.get('month', int(datetime.datetime.now().strftime("%m")) - 1))
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
        month_number = '12'
        month = 12
        month_name = 'December'

        path = os.path.dirname(os.path.abspath(__file__))
        path2file = path + '/AIReports/' + str(instance.db_id) + '_ai_data.csv'

        filename = '{}_{}_{} Raw data.csv'.format(month_name, instance.reporting_year.name, instance.label)

        with open(path2file, 'r') as f:
            response = HttpResponse(f.read(), content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename=%s;' % filename
        return response
