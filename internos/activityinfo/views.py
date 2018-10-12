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


class ExportViewSet(LoginRequiredMixin, ListView):

    model = ActivityReport
    queryset = ActivityReport.objects.all()

    # def get_queryset(self):
    #     if not self.request.user.is_staff:
    #         return self.queryset.filter(partner=self.request.user.partner)
    #     return self.queryset

    def get(self, request, *args, **kwargs):
        ai_id = self.request.GET.get('ai_id', 0)
        month = self.request.GET.get('month', 0)

        qs = self.get_queryset()
        if ai_id:
            qs = qs.filter(database_id=ai_id)
        if month:
            qs = qs.filter(month_name=month)

        headers = {

        }

        qs = qs.values(
            'end_date',
            'form',
            'form_category',
            'indicator_category',
            'indicator_id',
            'indicator_name',
            'indicator_units',
            'indicator_value',
            'location_adminlevel_cadastral_area',
            'location_adminlevel_cadastral_area_code',
            'location_adminlevel_caza',
            'location_adminlevel_caza_code',
            'location_adminlevel_governorate',
            'location_adminlevel_governorate_code',
            'governorate',
            'location_alternate_name',
            'location_latitude',
            'location_longitude',
            'location_name',
            'partner_description',
            'partner_id',
            'partner_label',
            'project_description',
            'project_label',
            'lcrp_appeal',
            'funded_by',
            'report_id',
            'site_id',
            'start_date',
            'outreach_platform',
            'database_id',
            'database',
            'month_name',
        )

        # return render_to_csv_response(qs, field_header_map=headers)
        return render_to_csv_response(qs)
