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
from .models import PartnerOrganization, Engagement, Travel, TravelType, TravelActivity
from internos.users.models import Section
from internos.activityinfo.models import Database


class PartnerProfileView(TemplateView):

    template_name = 'etools/partner_profile.html'

    def get_context_data(self, **kwargs):
        databases = Database.objects.filter(reporting_year__current=True).exclude(ai_id=10240).order_by('label')
        engagements = Engagement.objects.all()
        spot_checks = engagements.filter(engagement_type='sc')
        audits = engagements.filter(engagement_type='audit')
        micro_assessments = engagements.filter(engagement_type='ma')
        special_audits = engagements.filter(engagement_type='sa')

        travels = Travel.objects.all()
        programmatic_visits = travels.filter(travel_type='programmatic visit', start_date__year='2019')
        # programmatic_visits = TravelActivity.objects.filter(travel_type='programmatic visit', travel__end_date__year=2019)
        # programmatic_visits = TravelActivity.objects.filter(Q(travel_type='programmatic visit') | Q(travel_type='Programmatic Visit')).filter(travel__start_date__year='2019')
        # programmatic_visits = TravelActivity.objects.filter(Q(travel_type='programmatic visit') | Q(travel_type='Programmatic Visit'))
        # programmatic_visits = TravelActivity.objects.filter(travel_type=TravelType.PROGRAMME_MONITORING)

        partners_info = []
        # partners = PartnerOrganization.objects.exclude(interventions__isnull=False).exclude(hidden=True).exclude(deleted_flag=True)
        partners = PartnerOrganization.objects.exclude(hidden=True).exclude(deleted_flag=True)
        for partner in partners.iterator():
            partners_info.append(
                partner.detailed_info
            )

        return {
            'databases': databases,
            'partners': partners,
            'nbr_partners': partners.count(),
            'nbr_spot_checks': spot_checks.count(),
            'nbr_audits': audits.count(),
            'nbr_micro_assessments': micro_assessments.count(),
            'nbr_special_audits': special_audits.count(),
            'programmatic_visits': programmatic_visits.count(),
            'partners_info': partners_info
        }
