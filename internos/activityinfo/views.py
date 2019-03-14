from __future__ import absolute_import, unicode_literals

import datetime
from django.db.models import Q
from django.views.generic import ListView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse

from internos.backends.djqscsv import render_to_csv_response
from braces.views import GroupRequiredMixin, SuperuserRequiredMixin
from .models import ActivityReport, ActivityReportLive, Database, Indicator, Partner
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
            'selected_filter': selected_filter
        }


class LiveReportView(TemplateView):

    template_name = 'activityinfo/live.html'

    def get_context_data(self, **kwargs):
        selected_partner = self.request.GET.get('partner', 0)
        selected_partner_name = self.request.GET.get('partner_name', 'All Partners')
        selected_governorate = self.request.GET.get('governorate', 0)
        selected_governorate_name = self.request.GET.get('governorate_name', 'All Governorates')

        today = datetime.date.today()
        first = today.replace(day=1)
        last_month = first - datetime.timedelta(days=1)
        month_number = last_month.strftime("%m")
        month = int(last_month.strftime("%m"))
        month_name = last_month.strftime("%B")

        ai_id = int(self.request.GET.get('ai_id', 0))
        databases = Database.objects.filter(reporting_year__current=True).exclude(ai_id=10240).order_by('label')

        database = Database.objects.get(id=ai_id)
        report = ActivityReportLive.objects.filter(database=database)
        if database.is_funded_by_unicef:
            report = report.filter(funded_by__contains='UNICEF')

        partners = report.values('partner_ai__name', 'partner_id').distinct()
        governorates = report.values('location_adminlevel_governorate_code', 'location_adminlevel_governorate').distinct()
        master_indicators = Indicator.objects.filter(master_indicator=True, activity__database=database).order_by('id')

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
        }


class HPMView(TemplateView):

    template_name = 'activityinfo/hpm.html'

    def get_context_data(self, **kwargs):

        today = datetime.date.today()
        first = today.replace(day=1)
        last_month = first - datetime.timedelta(days=1)
        month_number = last_month.strftime("%m")
        month = int(last_month.strftime("%m"))
        month_name = last_month.strftime("%B")

        databases = Database.objects.filter(reporting_year__current=True).exclude(ai_id=10240).order_by('label')

        indicators = Indicator.objects.filter(hpm_indicator=True)
        sections = Section.objects.filter(have_hpm_indicator=True)

        return {
            'indicators': indicators,
            'sections': sections,
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
        month = int(last_month.strftime("%m"))
        month_name = last_month.strftime("%B")
        month = int(self.request.GET.get('month', month))

        filename = "HPM Table {} 2019.docx".format(month_name)

        new_file = update_hpm_table_docx(self.queryset, month, filename)

        with open(new_file, 'rb') as fh:
            response = HttpResponse(
                fh.read(),
                content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )
            response['Content-Disposition'] = 'attachment; filename=' + filename
        return response


class ExportViewSet(ListView):

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
