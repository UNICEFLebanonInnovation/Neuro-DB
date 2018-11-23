from __future__ import absolute_import, unicode_literals

import datetime
from django.db.models import Q
from django.views.generic import ListView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from internos.backends.djqscsv import render_to_csv_response
from braces.views import GroupRequiredMixin, SuperuserRequiredMixin
from .models import ActivityReport, Database


class IndexView(LoginRequiredMixin,
                TemplateView):

    template_name = 'activityinfo/dashboard.html'

    def get_context_data(self, **kwargs):
        month_name = self.request.GET.get('month', datetime.datetime.now().strftime("%B"))
        ai_id = int(self.request.GET.get('ai_id', 0))
        databases = Database.objects.all()

        if ai_id:
            database = Database.objects.get(ai_id=ai_id)
        else:
            section = self.request.user.section
            database = Database.objects.get(section=section)

        report = ActivityReport.objects.filter(database=database, month_name=month_name)
        months = ActivityReport.objects.values('month_name').distinct()
        partners = report.values('partner_id').distinct().count()
        activity_categories = report.values('form_category').distinct().count()
        activities = report.values('form').distinct().count()
        indicators = report.values('indicator_name').distinct().count()
        unicef_funds = report.filter(funded_by__contains='UNICEF').values('funded_by').count()
        not_reported = report.filter(Q(indicator_value__isnull=True) | Q(indicator_value='')).count()

        return {
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


class ReportView(LoginRequiredMixin,
                 TemplateView):

    template_name = 'activityinfo/report.html'

    def get_context_data(self, **kwargs):
        month_name = self.request.GET.get('month', datetime.datetime.now().strftime("%B"))
        ai_id = int(self.request.GET.get('ai_id', 0))
        databases = Database.objects.all()

        if ai_id:
            database = Database.objects.get(ai_id=ai_id)
        else:
            section = self.request.user.section
            database = Database.objects.get(section=section)

        report = ActivityReport.objects.filter(database=database, month_name=month_name)
        months = ActivityReport.objects.values('month_name').distinct()
        partners = report.values('partner_label', 'partner_id').distinct()
        governorates = report.values('location_adminlevel_governorate').distinct()
        activity_categories = report.values('form_category').distinct().count()
        activities = report.values('form').distinct().count()
        indicators = report.values('indicator_name').distinct().count()
        unicef_funds = report.filter(funded_by__contains='UNICEF').values('funded_by').count()
        not_reported = report.filter(Q(indicator_value__isnull=True) | Q(indicator_value='')).count()

        return {
            'month_name': month_name,
            'months': months,
            'months_nbr': months.count(),
            'database': database,
            'databases': databases,
            'partners': partners,
            'governorates': governorates,
            'activity_categories': activity_categories,
            'activities': activities,
            'not_reported': not_reported,
            'indicators': indicators,
            'unicef_funds': unicef_funds
        }


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    print(columns)
    print(cursor.fetchall())
    print([
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ])


class _Echo(object):
    """An object that implements just the write method of the file-like
    interface.
    """
    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value


class ExportViewSet(LoginRequiredMixin, ListView):

    model = ActivityReport
    queryset = ActivityReport.objects.all()

    def get_queryset(self):
        return self.queryset.filter(funded_by='UNICEF')

    def get(self, request, *args, **kwargs):

        ai_id = self.request.GET.get('ai_id', 0)
        month = self.request.GET.get('month', 0)
        report_format = self.request.GET.get('format', 0)
        filename = 'export_1.csv'

        instance = Database.objects.get(ai_id=ai_id)
        report_mapping = getattr(instance, report_format)

        qs = self.get_queryset()
        if ai_id:
            qs = qs.filter(database_id=ai_id)
        if month:
            qs = qs.filter(month_name=month)

        meta = {
            'file': '/{}/{}.{}'.format('tmp', instance.name, 'csv'),
            'queryset': qs,
            'fields': report_mapping.keys(),
            'header': report_mapping.values()
        }
        from internos.backends.gistfile import get_model_as_csv_file_response
        return get_model_as_csv_file_response(meta, content_type='text/csv')

        # data = ActivityReport.objects.raw('SELECT * FROM activityinfo_activityreport')
        # cursor = connection.cursor()
        # cursor.execute('SELECT * FROM activityinfo_activityreport LIMIT 1')
        # qs = cursor.fetchall()
        # print(cursor.fetchall())
        # qs = dictfetchall(cursor)
        # print(qs)

        # qs = self.get_queryset()
        # if ai_id:
        #     qs = qs.filter(database_id=ai_id)
        # if month:
        #     qs = qs.filter(month_name=month)
        #
        # qs = qs[:1]
        # report_mapping = [col[0] for col in cursor.description]
        # print(report_mapping)
        # print(qs)

        # response_args = {'content_type': 'text/csv'}
        # response = HttpResponse(**response_args)
        # extract(response, qs, report_mapping, filename)

        # response = StreamingHttpResponse(
        #     extract(_Echo(), qs, report_mapping, filename, **kwargs), **response_args)
        #
        # response['Content-Disposition'] = 'attachment; filename=%s;' % filename
        # response['Cache-Control'] = 'no-cache'
        #
        # return response

        # headers = report_mapping
        # print(type(headers.keys()))
        # print(', '.join(headers.keys()))
        # values = "', '".join(headers.keys())
        # values = "'"+values+"'"
        # print(values)
        # qs = qs.values([values])
        # qs = qs.values('partner_label', 'indicator_name', 'location_adminlevel_governorate', 'indicator_id', 'start_date', 'indicator_value')
        # qs = qs.extra(select={'partner_label, indicator_name, location_adminlevel_governorate, indicator_id, start_date, indicator_value'})
        # qs = qs.extra(select=headers.keys())

        # qs = qs.values(
        #     'end_date',
        #     'form',
        #     'form_category',
        #     'indicator_category',
        #     'indicator_id',
        #     'indicator_name',
        #     'indicator_units',
        #     'indicator_value',
        #     'location_adminlevel_cadastral_area',
        #     'location_adminlevel_cadastral_area_code',
        #     'location_adminlevel_caza',
        #     'location_adminlevel_caza_code',
        #     'location_adminlevel_governorate',
        #     'location_adminlevel_governorate_code',
        #     'governorate',
        #     'location_alternate_name',
        #     'location_latitude',
        #     'location_longitude',
        #     'location_name',
        #     'partner_description',
        #     'partner_id',
        #     'partner_label',
        #     'project_description',
        #     'project_label',
        #     'lcrp_appeal',
        #     'funded_by',
        #     'report_id',
        #     'site_id',
        #     'start_date',
        #     'outreach_platform',
        #     'database_id',
        #     'database',
        #     'month_name',
        # )

        # return render_to_csv_response(qs, field_header_map=headers)
        # return render_to_csv_response(qs)
        # return render_to_csv_response(qs, field_order=True, field_header_map=report_mapping)
