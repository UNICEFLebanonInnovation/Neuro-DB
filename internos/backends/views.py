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
from datetime import date

class HomeView(TemplateView):
    template_name = 'pages/index.html'

    def get_context_data(self, **kwargs):
        from internos.survey.models import EconomicReporting
        from internos.activityinfo.models import ReportingYear,Database


        year = date.today().year
        instance = ReportingYear.objects.get(current=True)
        reporting_year = self.request.GET.get('rep_year', instance.year)
        databases = Database.objects.filter(reporting_year__name=reporting_year,
                                            display=True).exclude(ai_id=10240).order_by('label')
      
        reports = EconomicReporting.objects.all().order_by('-reporting_date')

        official_rates = reports.filter(item_id=1)  # .aggregate(Max('reporting_date'))
        official_rate = official_rates.first().item_price
        official_rate_prev = official_rates[1].item_price
        official_rate_per = round((official_rate.amount - official_rate_prev.amount) / official_rate.amount * 100, 2)

        market_rates = reports.filter(item_id=2)  # .aggregate(Max('reporting_date'))
        market_rate = market_rates.first().item_price
        market_rate_prev = market_rates[1].item_price
        market_rate_per = round((market_rate.amount - market_rate_prev.amount) / market_rate.amount * 100, 2)
       

        bdl_rates = reports.filter(item_id=3)  # .aggregate(Max('reporting_date'))
        bdl_rate = bdl_rates.first().item_price
        bdl_rate_prev = bdl_rates[1].item_price
        bdl_rate_per = round((bdl_rate.amount - bdl_rate_prev.amount) / bdl_rate.amount * 100, 2)
        bdl_percentage_status = True if bdl_rate_per > 0 else False

        if self.request.user.is_authenticated:
               template = "base2.html";
        else:        
               template = "base_empty.html";



        return {
           'official_rate': official_rate,
           'official_rate_per':official_rate_per,
           'market_rate': market_rate,
           'market_rate_per': market_rate_per,
           'bdl_rate': bdl_rate,
           'bdl_percentage_status': bdl_percentage_status,
           'bdl_rate_per': bdl_rate_per,
           'ai_databases': databases,
           'reporting_year': reporting_year,
           'template':template
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
