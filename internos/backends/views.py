from __future__ import absolute_import, unicode_literals

import os
import json
import datetime
import calendar
from django.db.models import Q, Sum
from django.views.generic import ListView, TemplateView, FormView
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.http import HttpResponseRedirect


class HomeView(TemplateView):
    template_name = 'pages/index.html'

    def get_context_data(self, **kwargs):

        return {
        }


class DashboardView(TemplateView):
    template_name = 'pages/dashboard.html'

    def get_context_data(self, **kwargs):
        from internos.etools.models import PCA
        from internos.activityinfo.models import Indicator
        from internos.etools.utils import get_interventions_details

        now = datetime.datetime.now()

        interventions = PCA.objects.filter(end__year=now.year, status=PCA.ACTIVE)
        partners = PCA.objects.filter(end__year=now.year, status=PCA.ACTIVE).values('partner_name').distinct()

        donors_set = PCA.objects.filter(end__year=now.year,
                                        status=PCA.ACTIVE,
                                        donors__isnull=False,
                                        donors__len__gt=0).values('number', 'donors').distinct()

        donors = {}
        for item in donors_set:
            for donor in item['donors']:
                if donor not in donors:
                    donors[donor] = donor

        indicators = Indicator.objects.filter(activity__database__reporting_year__year=now.year,
                                              hpm_indicator=True,
                                              master_indicator=True).order_by('sequence')

        locations = get_interventions_details(interventions)

        return {
            'interventions': interventions.count(),
            'donors': len(donors),
            'partners': partners.count(),
            'indicators': indicators,
            'locations': locations
        }
