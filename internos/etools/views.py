from __future__ import absolute_import, unicode_literals

import os
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
        databases = Database.objects.filter(reporting_year__current=True).exclude(ai_id=10240).order_by('label')

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
            'databases': databases,
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


class InterventionsView(TemplateView):

    template_name = 'etools/interventions.html'

    def get_context_data(self, **kwargs):

        databases = Database.objects.filter(reporting_year__current=True).exclude(ai_id=10240).order_by('label')

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
            'databases': databases,
            'locations': locations,
            'nbr_interventions': interventions.count(),
            'nbr_active_interventions': active_interventions.count(),
            'nbr_pds': interventions_pd.count(),
            'nbr_active_pds': active_interventions_pd.count(),
            'nbr_sffas': interventions_sffa.count(),
            'nbr_active_sffas': active_interventions_sffa.count(),
        }


class TripsMonitoringView(TemplateView):

    template_name = 'etools/trips_monitoring.html'

    def get_context_data(self, **kwargs):
        now = datetime.datetime.now()
        travel_status = self.request.GET.get('travel_status', 'all')

        databases = Database.objects.filter(reporting_year__current=True).exclude(ai_id=10240).order_by('label')
        # sections = Section.objects.filter(etools=True)
        sections = Section.objects.filter()
        offices = Office.objects.all()

        visits = TravelActivity.objects.filter(travel_type=TravelType.PROGRAMME_MONITORING)
        # visits = TravelActivity.objects.filter(travel_type='programmatic visit', travel__start_date__year=now.year)

        if travel_status == 'all':
            trips = visits.exclude(travel__status=Travel.CANCELLED).exclude(travel__status=Travel.REJECTED)
        else:
            trips = visits.filter(travel__status=travel_status)

        programmatic_visits = visits.exclude(travel__status=Travel.CANCELLED).exclude(travel__status=Travel.REJECTED)
        programmatic_visits_planned = visits.filter(travel__status=Travel.PLANNED)
        programmatic_visits_submitted = visits.filter(travel__status=Travel.SUBMITTED)
        programmatic_visits_approved = visits.filter(travel__status=Travel.APPROVED)
        programmatic_visits_completed = visits.filter(travel__status=Travel.COMPLETED)

        trip_details = get_trip_details(trips)

        return {
            'databases': databases,
            'sections': sections,
            'offices': offices,
            'trip_details': trip_details,
            'travel_status': travel_status,
            'programmatic_visits': programmatic_visits.count(),
            'programmatic_visits_planned': programmatic_visits_planned.count(),
            'programmatic_visits_submitted': programmatic_visits_submitted.count(),
            'programmatic_visits_approved': programmatic_visits_approved.count(),
            'programmatic_visits_completed': programmatic_visits_completed.count(),
        }


class HACTView(TemplateView):

    template_name = 'etools/hact.html'

    def get_context_data(self, **kwargs):
        databases = Database.objects.filter(reporting_year__current=True).exclude(ai_id=10240).order_by('label')

        partners = PartnerOrganization.objects.exclude(hidden=True).exclude(deleted_flag=True)

        partners_info = get_partner_profile_details()

        return {
            'databases': databases,
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
