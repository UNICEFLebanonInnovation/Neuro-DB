from __future__ import absolute_import, unicode_literals

import os
import json
import random
import datetime
import calendar
from django.db.models import Q
from django.views.generic import ListView,TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from rest_framework import status
from rest_framework import viewsets, mixins, permissions

from internos.backends.djqscsv import render_to_csv_response
from braces.views import GroupRequiredMixin, SuperuserRequiredMixin
from .models import PartnerOrganization, PCA, Engagement, Travel, TravelType, TravelActivity, DonorFunding
from .utils import get_partner_profile_details, get_trip_details, get_interventions_details
from .serializers import PartnerOrganizationSerializer
from internos.users.models import Section, Office
from internos.activityinfo.utils import load_reporting_map
from internos.activityinfo.models import ActivityReport


class PartnershipView(LoginRequiredMixin,TemplateView):

    template_name = 'etools/partnerships.html'

    def get_context_data(self, **kwargs):

        return {}


class DonorMappingView(LoginRequiredMixin,TemplateView):

    template_name = 'etools/donor_mapping.html'

    def get_context_data(self, **kwargs):

        now = datetime.datetime.now()

        donors_set = PCA.objects.filter(end__year=now.year,
                                        donors__isnull=False,
                                        donors__len__gt=0).values('donors_set').distinct()

        donors = {}
        for item in donors_set:
            for donor in item['donors_set']:
                donors[donor['donor_code']] = {
                    'code': donor['donor_code'],
                    'name': donor['donor']
                }

        return {
            'donors': donors.values(),
        }


class DonorInterventionsView(LoginRequiredMixin,TemplateView):

    template_name = 'etools/interventions_block.html'

    def get_context_data(self, **kwargs):

        selected_donor = self.request.GET.get('donor', 'G45301')
        now = datetime.datetime.now()

        years = (now.year, now.year - 1)

        interventions = PCA.objects.filter(start__year__in=years).extra(where=["'"+selected_donor+"' = ANY (donor_codes)"]).order_by('-start')

        return {
            'interventions': interventions,
            'count': interventions.count(),
            'selected_donor': selected_donor
        }


def load_donor_locations(request):
    selected_donor = request.GET.get('donor', 'G45301')

    now = datetime.datetime.now()

    years = (now.year, now.year - 1)

    interventions = PCA.objects.filter(start__year__in=years).extra(where=["'"+selected_donor+"' = ANY (donor_codes)"]).order_by('-start')

    locations = get_interventions_details(interventions)

    return JsonResponse({'result': locations})


class DonorProgrammeResultsView(LoginRequiredMixin,TemplateView):

    template_name = 'etools/donor_results.html'

    def get_context_data(self, **kwargs):

        selected_donor = self.request.GET.get('donor', 'G45301')

        now = datetime.datetime.now()

        years = (now.year, now.year - 1)

        interventions = PCA.objects.filter(start__year__in=years).extra(where=["'"+selected_donor+"' = ANY (donor_codes)"]).order_by('-start')

        indicators = ActivityReport.objects.filter(programme_document__in=interventions,
                                                   ai_indicator__main_master_indicator__master_indicator=True)\
            .values('ai_indicator__main_master_indicator__id',
                    'ai_indicator__main_master_indicator__measurement_type',
                    'ai_indicator__main_master_indicator__name',
                    'ai_indicator__activity__database__section__logo',
                    'ai_indicator__main_master_indicator__units',
                    'ai_indicator__main_master_indicator__reporting_level',
                    'ai_indicator__main_master_indicator__target',
                    'ai_indicator__main_master_indicator__status_color',
                    'ai_indicator__main_master_indicator__status',
                    'ai_indicator__main_master_indicator__cumulative_values',
                    'ai_indicator__main_master_indicator__values_tags').distinct()

        return {
            'indicators': indicators,
            'count': indicators.count(),
        }


class DonorFundingView(LoginRequiredMixin,TemplateView):
    template_name = 'etools/donor_funding.html'

    def get_context_data(self, **kwargs):

        selected_donor = self.request.GET.get('donor', 'G45301')

        data_set1 = {}
        data_category1 = DonorFunding.objects.filter(donor_code=selected_donor).order_by('year')
        for item in data_category1:
            if item.donor_code not in data_set1:
                data_set1[item.donor_code] = {}
                data_set1[item.donor_code] = {
                    'name': item.donor,
                    'data': []
                }
            data_set1[item.donor_code]['data'].append((item.year, item.total))

        return {
            'data_set1': json.dumps(data_set1.values()),
        }


class DonorMapping2View(LoginRequiredMixin,TemplateView):

    template_name = 'etools/donor_mapping.html'

    def get_context_data(self, **kwargs):

        now = datetime.datetime.now()
        selected_partners = self.request.GET.get('partners', 0)
        selected_governorates = self.request.GET.get('governorates', 0)
        selected_donors = self.request.GET.get('donors', 0)

        report = ActivityReport.objects.filter()

        rows = load_reporting_map(partner=selected_partners, governorate=selected_governorates,
                                  donor=selected_donors)

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

        donors_set = PCA.objects.filter(end__year=now.year,
                                        donors__isnull=False,
                                        donors__len__gt=0).values('number', 'donors').distinct()

        donors = {}
        for item in donors_set:
            for donor in item['donors']:
                donors[donor] = donor

        return {
            'selected_partners': selected_partners,
            'selected_governorates': selected_governorates,
            'selected_donors': selected_donors,
            'partners': partners,
            'governorates': governorates,
            'donors': donors,
            'locations': locations,
            'locations_count': ctr
        }


class PartnerProfileView(LoginRequiredMixin,TemplateView):

    template_name = 'etools/partner_profile.html'

    def get_context_data(self, **kwargs):

        partners_info = []
        sections = {}
        donors = {}
        now = datetime.datetime.now()
        # sections = Section.objects.filter(etools=True)
        donors_set = PCA.objects.filter(donors__len__gt=0).values('donors')
        for item in donors_set:
            for donor in item['donors']:
                donors[donor] = donor

        sections_set = PCA.objects.filter(section_names__len__gt=0).values('section_names')
        for item in sections_set:
            for section in item['section_names']:
                sections[section] = section

        years = (now.year, now.year - 1)
        engagements = Engagement.objects.filter(start_date__year__in=years).exclude(status=Engagement.CANCELLED)
        # engagements = Engagement.objects.exclude(status=Engagement.CANCELLED)
        spot_checks = engagements.filter(engagement_type='sc')
        audits = engagements.filter(engagement_type='audit')
        micro_assessments = engagements.filter(engagement_type='ma')
        special_audits = engagements.filter(engagement_type='sa')

        interventions = PCA.objects.filter(end__year__in=years).exclude(status=PCA.CANCELLED)
        # interventions = PCA.objects.filter(end__year=now.year).exclude(status=PCA.CANCELLED)
        active_interventions = interventions.filter(status=PCA.ACTIVE)

        interventions_pd = interventions.filter(document_type=PCA.PD)
        active_interventions_pd = interventions_pd.filter(status=PCA.ACTIVE)

        interventions_sffa = interventions.filter(document_type=PCA.SSFA)
        active_interventions_sffa = interventions_sffa.filter(status=PCA.ACTIVE)

        # visits = TravelActivity.objects.filter(travel_type=TravelType.PROGRAMME_MONITORING, travel__start_date__year=now.year)
        visits = TravelActivity.objects.filter(travel_type=TravelType.PROGRAMME_MONITORING, travel__start_date__year__in=years)
        programmatic_visits = visits.exclude(travel__status=Travel.CANCELLED).exclude(travel__status=Travel.REJECTED)
        programmatic_visits_planned = visits.filter(travel__status=Travel.PLANNED)
        programmatic_visits_submitted = visits.filter(travel__status=Travel.SUBMITTED)
        programmatic_visits_approved = visits.filter(travel__status=Travel.APPROVED)
        programmatic_visits_completed = visits.filter(travel__status=Travel.COMPLETED)

        partners = PartnerOrganization.objects.exclude(hidden=True).exclude(deleted_flag=True)

        partners_info = get_partner_profile_details()

        return {
            'donors': donors,
            'sections': sections,
            'partners': partners,
            'nbr_interventions': interventions.count(),
            'nbr_active_interventions': active_interventions.count(),
            'nbr_pds': interventions_pd.count(),
            'nbr_active_pds': active_interventions_pd.count(),
            'nbr_sffas': interventions_sffa.count(),
            'nbr_active_sffas': active_interventions_sffa.count(),
            'nbr_partners': partners.count(),
            'nbr_spot_checks': spot_checks.count(),
            'nbr_audits': audits.count(),
            'nbr_micro_assessments': micro_assessments.count(),
            'nbr_special_audits': special_audits.count(),
            'programmatic_visits': programmatic_visits.count(),
            'programmatic_visits_planned': programmatic_visits_planned.count(),
            'programmatic_visits_submitted': programmatic_visits_submitted.count(),
            'programmatic_visits_approved': programmatic_visits_approved.count(),
            'programmatic_visits_completed': programmatic_visits_completed.count(),
            'partners_info': partners_info
        }


class PartnerProfileMapView(LoginRequiredMixin,TemplateView):

    template_name = 'etools/partner_profile_map.html'

    def get_context_data(self, **kwargs):

        selected_partner = self.request.GET.get('partner_id', 0)
        partner = PartnerOrganization.objects.get(id=selected_partner)

        now = datetime.datetime.now()

        data_set = PCA.objects.filter(partner_id=partner.etl_id,
                                      end__year=now.year).exclude(status=PCA.CANCELLED)

        # locations = get_interventions_details(data_set)

        from django.db import connection
        cursor = connection.cursor()

        cursor.execute(
            "SELECT DISTINCT ar.site_id, ar.location_name, ar.location_longitude, ar.location_latitude, "
            "ar.indicator_units, ar.location_adminlevel_governorate, ar.location_adminlevel_caza, "
            "ar.location_adminlevel_caza_code, ar.location_adminlevel_cadastral_area, "
            "ar.location_adminlevel_cadastral_area_code, ar.partner_label, ai.name AS indicator_name, "
            "ai.cumulative_values ->> 'months'::text AS cumulative_value "
            "FROM public.activityinfo_indicator ai "
            "INNER JOIN public.activityinfo_activityreport ar ON ai.id = ar.ai_indicator_id "
            "INNER JOIN public.activityinfo_activity aa ON aa.id = ai.activity_id "
            "INNER JOIN public.etools_pca pmp ON pmp.id = aa.programme_document_id "
            "INNER JOIN public.etools_partnerorganization po ON po.id = pmp.partner_id "
            "WHERE pmp.partner_id = %s ",
            [int(selected_partner)])
        rows = cursor.fetchall()

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
        # print(locations)

        return {
            'selected_partner': selected_partner,
            'partner': partner,
            'locations': locations,
        }


class InterventionsView(LoginRequiredMixin,TemplateView):

    template_name = 'etools/interventions.html'

    def get_context_data(self, **kwargs):

        document_type = self.request.GET.get('document_type', 'all')
        status = self.request.GET.get('status', 'all')
        now = datetime.datetime.now()

        interventions = PCA.objects.filter(end__year=now.year).exclude(status=PCA.CANCELLED)
        active_interventions = interventions.filter(status=PCA.ACTIVE)

        interventions_pd = interventions.filter(document_type=PCA.PD)
        active_interventions_pd = interventions_pd.filter(status=PCA.ACTIVE)

        interventions_sffa = interventions.filter(document_type=PCA.SSFA)
        active_interventions_sffa = interventions_sffa.filter(status=PCA.ACTIVE)

        data_set = PCA.objects.filter(end__year=now.year).exclude(status=PCA.CANCELLED)

        if not document_type == 'all':
            data_set = data_set.filter(document_type=document_type)

        if status == 'active':
            data_set = data_set.filter(status=PCA.ACTIVE)

        locations = get_interventions_details(data_set)

        return {
            'locations': locations,
            'nbr_interventions': interventions.count(),
            'nbr_active_interventions': active_interventions.count(),
            'nbr_pds': interventions_pd.count(),
            'nbr_active_pds': active_interventions_pd.count(),
            'nbr_sffas': interventions_sffa.count(),
            'nbr_active_sffas': active_interventions_sffa.count(),
        }


class InterventionExportViewSet(ListView):

    model = PCA
    queryset = PCA.objects.all()

    def get(self, request, *args, **kwargs):

        now = datetime.datetime.now()

        interventions = PCA.objects.filter(end__year=now.year).exclude(status=PCA.CANCELLED)
        locations = get_interventions_details(interventions, all_locations=True, json_dumps=False)
        # print(locations)

        filename = "extraction.csv"

        fields = locations[0].keys()
        header = locations[0].values()
        meta = {
            'file': filename,
            # 'file': '/{}/{}'.format('tmp', filename),
            'queryset': locations,
            'fields': fields,
            'header': fields
        }
        from internos.backends.gistfile import get_model_as_csv_file_response
        return get_model_as_csv_file_response(meta, content_type='text/csv', filename=filename)


class TripsMonitoringView(LoginRequiredMixin,TemplateView):

    template_name = 'etools/trip_monitoring2.html'

    def get_context_data(self, **kwargs):
        now = datetime.datetime.now()
        travel_status = self.request.GET.get('travel_status', 0)
        selected_month = self.request.GET.get('month', 0)
        selected_section = self.request.GET.get('section', 0)
        selected_year = self.request.GET.get('year', 0)
        selected_partner = self.request.GET.get('partner', 0)
        selected_donor = self.request.GET.get('donor', 0)

        sections = Section.objects.filter(etools=True)
        offices = Office.objects.all()
        donors_set = PCA.objects.filter(end__year=now.year,
                                        donors__isnull=False,
                                        donors__len__gt=0).values('number', 'donors').distinct()

        donors = {}
        for item in donors_set:
            for donor in item['donors']:
                donors[donor] = donor

        visits_no_partner = TravelActivity.objects.filter(travel_type=TravelType.PROGRAMME_MONITORING,
                                                          travel__start_date__year=now.year,
                                                          partner__isnull=True)\
            .exclude(travel__status=Travel.CANCELLED).exclude(travel__status=Travel.REJECTED)

        visits = TravelActivity.objects.filter(travel_type=TravelType.PROGRAMME_MONITORING,
                                               travel__start_date__year=now.year,
                                               partner__isnull=False)\
            .exclude(travel__status=Travel.CANCELLED).exclude(travel__status=Travel.REJECTED)

        if selected_month and not selected_month == '0':
            visits = visits.filter(travel__start_date__month=selected_month)
        if selected_year and not selected_year == '0':
            visits = visits.filter(travel__start_date__year=selected_year)
        if selected_section and not selected_section == '0':
            visits = visits.filter(travel__section=selected_section)
        if selected_donor and not selected_donor == '0':
            pass
            # visits = visits.filter(partnership__donors__values__contains=selected_donor)

        partners = visits.values('partner_id', 'partner__name').distinct()

        trips = visits
        if travel_status and not travel_status == '0':
            trips = visits.filter(travel__status=travel_status)
        if travel_status == 'completed_report':
            trips = visits.filter(travel__have_hact__gt=0)

        programmatic_visits = visits
        programmatic_visits_planned = visits.filter(travel__status=Travel.PLANNED)
        programmatic_visits_submitted = visits.filter(travel__status=Travel.SUBMITTED)
        programmatic_visits_approved = visits.filter(travel__status=Travel.APPROVED)
        programmatic_visits_completed = visits.filter(travel__status=Travel.COMPLETED)
        programmatic_visits_completed_no_report = programmatic_visits_completed.filter(travel__have_hact=0)
        programmatic_visits_completed_report = programmatic_visits_completed.filter(travel__have_hact__gt=0)

        trip_details = get_trip_details(trips)

        months = []
        for i in range(1, 13):
            months.append({
                'month': i,
                'month_name': (datetime.date(2008, i, 1).strftime('%B'))
            })

        trips_per_month = {Travel.SUBMITTED: [], Travel.APPROVED: [], Travel.COMPLETED: []}

        for item in [Travel.SUBMITTED, Travel.APPROVED, Travel.COMPLETED]:
            instances = visits.filter(travel__status=item)
            for m in months:
                ctr = instances.filter(travel__start_date__month=m['month'])
                trips_per_month[item].append({
                    'time': '{}-{}-{}'.format(now.year, m['month'], now.day),
                    'y': ctr.count(),
                    # 'y': random.randint(1, 50),
                    'x': m['month_name'],
                    'type': item.upper()
                })

        trips_per_month = json.dumps(trips_per_month.values())

        return {
            'months': months,
            'sections': sections,
            'offices': offices,
            'partners': partners,
            'trip_details': trip_details,
            'travel_status': travel_status,
            'selected_month': selected_month,
            'selected_year': selected_year,
            'selected_section': selected_section,
            'selected_partner': selected_partner,
            'selected_donor': selected_donor,
            'trips_per_month': trips_per_month,
            'donors': donors,
            'programmatic_visits': programmatic_visits.count(),
            'programmatic_visits_planned': programmatic_visits_planned.count(),
            'programmatic_visits_submitted': programmatic_visits_submitted.count(),
            'programmatic_visits_approved': programmatic_visits_approved.count(),
            'programmatic_visits_completed': programmatic_visits_completed.count(),
            'programmatic_visits_completed_report': programmatic_visits_completed_report.count(),
            'programmatic_visits_completed_no_report': programmatic_visits_completed_no_report.count()
        }


class HACTView(LoginRequiredMixin,TemplateView):

    template_name = 'etools/hact.html'

    def get_context_data(self, **kwargs):

        partners = PartnerOrganization.objects.exclude(hidden=True).exclude(deleted_flag=True)

        partners_info = get_partner_profile_details()

        return {
            'partners': partners,
            'partners_info': partners_info
        }


class CommentUpdateViewSet(mixins.RetrieveModelMixin,
                           mixins.UpdateModelMixin,
                           viewsets.GenericViewSet,
                           SuperuserRequiredMixin):
    """
    Provides API operations around a Enrollment record
    """
    model = PartnerOrganization
    queryset = PartnerOrganization.objects.all()
    serializer_class = PartnerOrganizationSerializer
    permission_classes = (permissions.IsAuthenticated,)
