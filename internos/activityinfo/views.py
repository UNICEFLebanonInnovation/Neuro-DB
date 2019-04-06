from __future__ import absolute_import, unicode_literals

import os
import datetime
import calendar
from django.db.models import Q
from django.views.generic import ListView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse

from internos.backends.djqscsv import render_to_csv_response
from braces.views import GroupRequiredMixin, SuperuserRequiredMixin
from .models import ActivityReport, LiveActivityReport, Database, Indicator, Partner
from internos.users.models import Section


class IndexView(TemplateView):

    template_name = 'activityinfo/index.html'

    def get_context_data(self, **kwargs):
        databases = Database.objects.filter(reporting_year__current=True).exclude(ai_id=10240).order_by('label')

        return {
            'databases': databases,
        }


class DashboardView(TemplateView):

    template_name = 'activityinfo/dashboard.html'

    def get_context_data(self, **kwargs):
        month = int(self.request.GET.get('month', int(datetime.datetime.now().strftime("%m")) - 1))
        month_name = self.request.GET.get('month', datetime.datetime.now().strftime("%B"))
        ai_id = int(self.request.GET.get('ai_id', 0))
        databases = Database.objects.filter(reporting_year__current=True).exclude(ai_id=10240).order_by('label')

        if ai_id:
            database = Database.objects.get(ai_id=ai_id)
        else:
            try:
                section = self.request.user.section
                database = Database.objects.get(section=section, reporting_year__current=True)
            except Exception:
                database = Database.objects.filter(reporting_year__current=True).first()

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
            'databases': databases,
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
        selected_partner_name = self.request.GET.get('partner_name', 'All Partners')
        selected_governorate = self.request.GET.get('governorate', 0)
        selected_governorate_name = self.request.GET.get('governorate_name', 'All Governorates')

        partner_info = {}
        today = datetime.date.today()
        first = today.replace(day=1)
        last_month = first - datetime.timedelta(days=1)
        month_number = last_month.strftime("%m")
        month = int(last_month.strftime("%m"))
        month_name = last_month.strftime("%B")

        ai_id = int(self.request.GET.get('ai_id', 0))
        databases = Database.objects.filter(reporting_year__current=True).exclude(ai_id=10240).order_by('label')

        if ai_id:
            database = Database.objects.get(ai_id=ai_id)
        else:
            try:
                section = self.request.user.section
                database = Database.objects.get(section=section, reporting_year__current=True)
            except Exception:
                database = Database.objects.filter(reporting_year__current=True).first()

        report = ActivityReport.objects.filter(database=database)
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

        if selected_partner or selected_governorate:
            selected_filter = True

        if selected_partner == '0' and selected_governorate == '0':
            selected_filter = False

        partners = report.values('partner_label', 'partner_id').distinct()
        governorates = report.values('location_adminlevel_governorate_code', 'location_adminlevel_governorate').distinct()

        master_indicators = Indicator.objects.filter(activity__database=database).order_by('sequence')
        if database.mapped_db:
            master_indicators = master_indicators.filter(Q(master_indicator=True) | Q(individual_indicator=True))

        none_ai_indicators = Indicator.objects.filter(activity__none_ai_database=database)

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
        for i in range(1, 13):
            months.append((i, datetime.date(2008, i, 1).strftime('%B')))

        return {
            'selected_partner': selected_partner,
            'selected_partner_name': selected_partner_name,
            'selected_governorate': selected_governorate,
            'selected_governorate_name': selected_governorate_name,
            'reports': report.order_by('id'),
            'month': month,
            'month_name': month_name,
            'month_number': month_number,
            'months': months,
            'database': database,
            'databases': databases,
            'partners': partners,
            'governorates': governorates,
            'master_indicators': master_indicators,
            'partner_info': partner_info,
            'selected_filter': selected_filter,
            'none_ai_indicators': none_ai_indicators
        }


class LiveReportView(TemplateView):

    template_name = 'activityinfo/live.html'

    def get_context_data(self, **kwargs):
        selected_filter = False
        selected_partner = self.request.GET.get('partner', 0)
        selected_partner_name = self.request.GET.get('partner_name', 'All Partners')
        selected_governorate = self.request.GET.get('governorate', 0)
        selected_governorate_name = self.request.GET.get('governorate_name', 'All Governorates')

        partner_info = {}
        today = datetime.date.today()
        day_number = today.strftime("%d")
        month_number = today.strftime("%m")
        month = int(today.strftime("%m"))
        month_name = today.strftime("%B")

        ai_id = int(self.request.GET.get('ai_id', 0))
        databases = Database.objects.filter(reporting_year__current=True).exclude(ai_id=10240).order_by('label')

        database = Database.objects.get(ai_id=ai_id)

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

        if selected_partner or selected_governorate:
            selected_filter = True

        if selected_partner == '0' and selected_governorate == '0':
            selected_filter = False

        partners = {}
        for partner in report.values('partner_label', 'partner_id').distinct():
            partners[partner['partner_id']] = partner['partner_label']
        governorates = {}
        for gov in report.values('location_adminlevel_governorate_code', 'location_adminlevel_governorate').distinct():
            governorates[gov['location_adminlevel_governorate_code']] = gov['location_adminlevel_governorate']

        master_indicators = Indicator.objects.filter(activity__database=database).order_by('sequence')
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
            'selected_partner': selected_partner,
            'selected_partner_name': selected_partner_name,
            'selected_governorate': selected_governorate,
            'selected_governorate_name': selected_governorate_name,
            'reports': report.order_by('id'),
            'month': month,
            'month_name': month_name,
            'month_number': month_number,
            'database': database,
            'databases': databases,
            'partners': partners,
            'governorates': governorates,
            'master_indicators': master_indicators,
            'selected_filter': selected_filter,
            'partner_info': partner_info,
            'day_number': day_number
        }


class HPMView(TemplateView):

    template_name = 'activityinfo/hpm.html'

    def get_context_data(self, **kwargs):

        today = datetime.date.today()
        first = today.replace(day=1)
        last_month = first - datetime.timedelta(days=1)
        day_number = int(today.strftime("%d"))
        month = int(self.request.GET.get('month', last_month.strftime("%m")))
        if day_number < 15:
            month = month - 1

        month_name = calendar.month_name[month]

        months = []
        for i in range(1, 13):
            months.append((datetime.date(2008, i, 1).strftime('%B')))

        databases = Database.objects.filter(reporting_year__current=True).exclude(ai_id=10240).order_by('label')

        return {
            'month_name': month_name,
            'month': month,
            'databases': databases,
        }


class HPMExportViewSet(ListView):

    model = Indicator
    queryset = Indicator.objects.filter(hpm_indicator=True)

    def get(self, request, *args, **kwargs):
        from .utils import update_hpm_table_docx

        today = datetime.date.today()
        first = today.replace(day=1)
        last_month = first - datetime.timedelta(days=1)
        month = int(self.request.GET.get('month', last_month.strftime("%m"))) - 1

        months = []
        for i in range(1, 13):
            months.append((datetime.date(2008, i, 1).strftime('%B')))

        filename = "HPM Table {} 2019.docx".format(months[month])

        new_file = update_hpm_table_docx(self.queryset, month, months[month], filename)

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

        path = os.path.dirname(os.path.abspath(__file__))
        path2file = path+'/AIReports/'+str(ai_id)+'_ai_data.csv'

        filename = '{}_{}_{} Raw data.csv'.format(month_name, instance.reporting_year.name, instance.label)

        with open(path2file, 'r') as f:
            response = HttpResponse(f.read(), content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename=%s;' % filename
        return response


class TestView(TemplateView):

    template_name = 'activityinfo/test.html'

    def get_context_data(self, **kwargs):
        from django.db import connection

        from internos.activityinfo.models import Indicator, ActivityReport, LiveActivityReport
        report_type = 'live'
        ai_db = Database.objects.get(ai_id=10169)

        last_month = int(datetime.datetime.now().strftime("%m"))

        if report_type == 'live':
            reports = LiveActivityReport.objects.filter(database_id=ai_db.ai_id)
            last_month = last_month + 1
        else:
            reports = ActivityReport.objects.filter(database_id=ai_db.ai_id)
        if ai_db.is_funded_by_unicef:
            reports = reports.filter(funded_by='UNICEF')

        indicators = Indicator.objects.filter(activity__database__ai_id=ai_db.ai_id).exclude(ai_id__isnull=True).only(
            'ai_indicator',
            'values_live',
            'values_gov_live',
            'values_partners_live',
            'values_partners_gov_live')

        partners = reports.values('partner_id').distinct().order_by('partner_id')
        governorates = reports.values('location_adminlevel_governorate_code').distinct().order_by('location_adminlevel_governorate_code')
        governorates1 = reports.values('location_adminlevel_governorate_code').distinct().order_by('location_adminlevel_governorate_code')
        reporting_month = str(last_month - 1)

        rows_months = {}
        rows_partners = {}
        rows_govs = {}
        rows_partners_govs = {}
        cursor = connection.cursor()
        for month in range(1, last_month):
            month = str(month)
            cursor.execute(
                "SELECT indicator_id, SUM(indicator_value) as indicator_value "
                "FROM activityinfo_liveactivityreport "
                "WHERE date_part('month', start_date) = %s AND database_id = %s AND funded_by = %s "
                "GROUP BY indicator_id",
                [month, '10169', 'UNICEF'])
            rows = cursor.fetchall()

            for row in rows:
                if row[0] not in rows_months:
                    rows_months[row[0]] = {}
                rows_months[row[0]][month] = row[1]

            cursor.execute(
                "SELECT indicator_id, SUM(indicator_value) as indicator_value, location_adminlevel_governorate_code "
                "FROM activityinfo_liveactivityreport "
                "WHERE date_part('month', start_date) = %s AND database_id = %s AND funded_by = %s "
                "GROUP BY indicator_id, location_adminlevel_governorate_code",
                [month, '10169', 'UNICEF'])
            rows = cursor.fetchall()

            for row in rows:
                if row[0] not in rows_govs:
                    rows_govs[row[0]] = {}
                key = "{}-{}".format(month, row[2])
                rows_govs[row[0]][key] = row[1]

            cursor.execute(
                "SELECT indicator_id, SUM(indicator_value) as indicator_value, partner_id "
                "FROM activityinfo_liveactivityreport "
                "WHERE date_part('month', start_date) = %s AND database_id = %s AND funded_by = %s "
                "GROUP BY indicator_id, partner_id",
                [month, '10169', 'UNICEF'])
            rows = cursor.fetchall()

            for row in rows:
                if row[0] not in rows_partners:
                    rows_partners[row[0]] = {}
                key = "{}-{}".format(month, row[2])
                rows_partners[row[0]][key] = row[1]

            cursor.execute(
                "SELECT indicator_id, SUM(indicator_value) as indicator_value, location_adminlevel_governorate_code, partner_id "
                "FROM activityinfo_liveactivityreport "
                "WHERE date_part('month', start_date) = %s AND database_id = %s AND funded_by = %s "
                "GROUP BY indicator_id, location_adminlevel_governorate_code, partner_id",
                [month, '10169', 'UNICEF'])
            rows = cursor.fetchall()

            for row in rows:
                if row[0] not in rows_partners_govs:
                    rows_partners_govs[row[0]] = {}
                key = "{}-{}-{}".format(month, row[2], row[3])
                rows_partners_govs[row[0]][key] = row[1]

        for indicator in indicators.iterator():
            if indicator.ai_indicator in rows_months:
                indicator.values_live = rows_months[indicator.ai_indicator]

            if indicator.ai_indicator in rows_partners:
                indicator.values_partners_live = rows_partners[indicator.ai_indicator]

            if indicator.ai_indicator in rows_govs:
                indicator.values_gov_live = rows_govs[indicator.ai_indicator]

            if indicator.ai_indicator in rows_partners_govs:
                indicator.values_partners_gov_live = rows_partners_govs[indicator.ai_indicator]

            indicator.save()

        # print(rows_data)
        # print(type(row))
        # print(type(row[0]))
        # print(row[0][0])
        # print(row)
        # qs_raw = LiveActivityReport.objects.raw(
        #     "SELECT id, indicator_id, SUM(indicator_value) as indicator_value FROM activityinfo_liveactivityreport "
        #     "WHERE date_part('month', start_date) = %s AND database_id = %s AND funded_by = %s "
        #     "GROUP BY indicator_id",
        #     [1, '10169', 'UNICEF'])
        #
        # print(qs_raw[0])

        # for indicator in indicators.iterator():
        #
        #     qs_raw = LiveActivityReport.objects.raw(
        #         "SELECT id FROM activityinfo_liveactivityreport "
        #         "WHERE indicator_id = %s AND funded_by = %s ",
        #         [indicator.ai_indicator, 'UNICEF'])
        #     try:
        #         count = qs_raw[0]
        #     except Exception as ex:
        #         continue
        #
        #     for month in range(1, last_month):
        #         month = str(month)
        #         result = 0
        #         qs_raw = LiveActivityReport.objects.raw(
        #             "SELECT id, SUM(indicator_value) as indicator_value FROM activityinfo_liveactivityreport "
        #             "WHERE date_part('month', start_date) = %s AND indicator_id = %s AND funded_by = %s "
        #             "GROUP BY id",
        #             [month, indicator.ai_indicator, 'UNICEF'])
        #         try:
        #             result = qs_raw[0].indicator_value
        #         except Exception:
        #             continue
        #
        #         if report_type == 'live':
        #             indicator.values_live[str(month)] = result
        #         else:
        #             if month == reporting_month:
        #                 indicator.values_hpm[reporting_month] = result
        #             indicator.values[str(month)] = result
        #
        #         for gov1 in governorates1:
        #             value = 0
        #             key = "{}-{}".format(month, gov1['location_adminlevel_governorate_code'])
        #
        #             qs_raw = LiveActivityReport.objects.raw(
        #                 "SELECT id, SUM(indicator_value) as indicator_value FROM activityinfo_liveactivityreport "
        #                 "WHERE date_part('month', start_date) = %s AND indicator_id = %s AND funded_by = %s "
        #                 "AND location_adminlevel_governorate_code = %s "
        #                 "GROUP BY id",
        #                 [month, indicator.ai_indicator, 'UNICEF', gov1['location_adminlevel_governorate_code']])
        #             try:
        #                 value = qs_raw[0].indicator_value
        #             except Exception:
        #                 pass
        #
        #             if report_type == 'live':
        #                 indicator.values_gov_live[str(key)] = value
        #             else:
        #                 indicator.values_gov[str(key)] = value
        #
        #         for partner in partners:
        #             value1 = 0
        #             key1 = "{}-{}".format(month, partner['partner_id'])
        #
        #             qs_raw = LiveActivityReport.objects.raw(
        #                 "SELECT id, SUM(indicator_value) as indicator_value FROM activityinfo_liveactivityreport "
        #                 "WHERE date_part('month', start_date) = %s AND indicator_id = %s AND funded_by = %s "
        #                 "AND partner_id = %s "
        #                 "GROUP BY id",
        #                 [month, indicator.ai_indicator, 'UNICEF', partner['partner_id']])
        #             try:
        #                 value1 = qs_raw[0].indicator_value
        #             except Exception:
        #                 continue
        #
        #             if report_type == 'live':
        #                 indicator.values_partners_live[str(key1)] = value1
        #             else:
        #                 indicator.values_partners[str(key1)] = value1
        #
        #             for gov in governorates:
        #                 value2 = 0
        #                 key2 = "{}-{}-{}".format(month, partner['partner_id'], gov['location_adminlevel_governorate_code'])
        #
        #                 qs_raw = LiveActivityReport.objects.raw(
        #                     "SELECT id, SUM(indicator_value) as indicator_value FROM activityinfo_liveactivityreport "
        #                     "WHERE date_part('month', start_date) = %s AND indicator_id = %s AND funded_by = %s "
        #                     "AND partner_id = %s AND location_adminlevel_governorate_code = %s "
        #                     "GROUP BY id",
        #                     [month, indicator.ai_indicator, 'UNICEF', partner['partner_id'], gov['location_adminlevel_governorate_code']])
        #                 try:
        #                     value2 = qs_raw[0].indicator_value
        #                 except Exception:
        #                     pass
        #
        #                 if report_type == 'live':
        #                     indicator.values_partners_gov_live[str(key2)] = value2
        #                 else:
        #                     indicator.values_partners_gov[str(key2)] = value2
        #
        #         indicator.save()

        return {

        }
