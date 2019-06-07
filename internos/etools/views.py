from __future__ import absolute_import, unicode_literals

import os
import json
import random
import datetime
import calendar
from django.db.models import Q
from django.views.generic import ListView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from rest_framework import status
from rest_framework import viewsets, mixins, permissions

from internos.backends.djqscsv import render_to_csv_response
from braces.views import GroupRequiredMixin, SuperuserRequiredMixin
from .models import PartnerOrganization, PCA, Engagement, Travel, TravelType, TravelActivity
from .utils import get_partner_profile_details, get_trip_details, get_interventions_details
from .serializers import PartnerOrganizationSerializer
from internos.users.models import Section, Office
from internos.activityinfo.models import Database


class PartnerProfileView(TemplateView):

    template_name = 'etools/partner_profile.html'

    def get_context_data(self, **kwargs):

        partners_info = []
        now = datetime.datetime.now()

        engagements = Engagement.objects.filter(start_date__year=now.year).exclude(status=Engagement.CANCELLED)
        spot_checks = engagements.filter(engagement_type='sc')
        audits = engagements.filter(engagement_type='audit')
        micro_assessments = engagements.filter(engagement_type='ma')
        special_audits = engagements.filter(engagement_type='sa')

        interventions = PCA.objects.filter(end__year=now.year).exclude(status=PCA.CANCELLED)
        active_interventions = interventions.filter(status=PCA.ACTIVE)

        interventions_pd = interventions.filter(document_type=PCA.PD)
        active_interventions_pd = interventions_pd.filter(status=PCA.ACTIVE)

        interventions_sffa = interventions.filter(document_type=PCA.SSFA)
        active_interventions_sffa = interventions_sffa.filter(status=PCA.ACTIVE)

        visits = TravelActivity.objects.filter(travel_type=TravelType.PROGRAMME_MONITORING, travel__start_date__year=now.year)
        programmatic_visits = visits.exclude(travel__status=Travel.CANCELLED).exclude(travel__status=Travel.REJECTED)
        programmatic_visits_planned = visits.filter(travel__status=Travel.PLANNED)
        programmatic_visits_submitted = visits.filter(travel__status=Travel.SUBMITTED)
        programmatic_visits_approved = visits.filter(travel__status=Travel.APPROVED)
        programmatic_visits_completed = visits.filter(travel__status=Travel.COMPLETED)

        partners = PartnerOrganization.objects.exclude(hidden=True).exclude(deleted_flag=True)

        partners_info = get_partner_profile_details()

        return {
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


class PartnerProfileMapView(TemplateView):

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

            locations[item[0]]['indicators'].append({
                'indicator_units': item[4].upper(),
                'partner_label': item[10],
                'indicator_name': item[11],
                'cumulative_value': "{:,}".format(round(float(item[12]), 1)),
            })

        locations = json.dumps(locations.values())
        # print(locations)

        return {
            'selected_partner': selected_partner,
            'partner': partner,
            'locations': locations,
        }


class InterventionsView(TemplateView):

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


class TripsMonitoringView(TemplateView):

    template_name = 'etools/trip_monitoring2.html'

    def get_context_data(self, **kwargs):
        now = datetime.datetime.now()
        travel_status = self.request.GET.get('travel_status', '')
        selected_month = self.request.GET.get('month', 0)

        sections = Section.objects.filter(etools=True)
        offices = Office.objects.all()

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

        partners = visits.values('partner_id', 'partner__name').distinct()

        trips = visits
        if travel_status:
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
            'trips_per_month': trips_per_month,
            'programmatic_visits': programmatic_visits.count(),
            'programmatic_visits_planned': programmatic_visits_planned.count(),
            'programmatic_visits_submitted': programmatic_visits_submitted.count(),
            'programmatic_visits_approved': programmatic_visits_approved.count(),
            'programmatic_visits_completed': programmatic_visits_completed.count(),
            'programmatic_visits_completed_report': programmatic_visits_completed_report.count(),
            'programmatic_visits_completed_no_report': programmatic_visits_completed_no_report.count()
        }


class HACTView(TemplateView):

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
