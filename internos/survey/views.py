from __future__ import absolute_import, unicode_literals

import os
import json
import datetime
import calendar
from django.db.models import Q, Sum, Max
from django.views.generic import ListView, TemplateView, FormView
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from datetime import date
from django.http import HttpResponseRedirect
from .models import EconomicReporting


class EconomicDashboardView(TemplateView):
    template_name = 'survey/economic_dashboard.html'

    def get_context_data(self, **kwargs):

        reports = EconomicReporting.objects.all().order_by('-reporting_date')

        official_rates = reports.filter(item_id=1)  # .aggregate(Max('reporting_date'))
        official_rate = official_rates.first().item_price
        official_rate_prev = official_rates[1].item_price
        official_rate_per = round((official_rate.amount - official_rate_prev.amount) / official_rate.amount * 100, 2)

        market_rates = reports.filter(item_id=2)  # .aggregate(Max('reporting_date'))
        market_rate = market_rates.first().item_price
        market_rate_prev = market_rates[1].item_price
        market_rate_per = round((market_rate.amount - market_rate_prev.amount) / market_rate.amount * 100, 2)
        market_percentage_status = True if market_rate_per > 0 else False

        bdl_rates = reports.filter(item_id=3)  # .aggregate(Max('reporting_date'))
        bdl_rate = bdl_rates.first().item_price
        bdl_rate_prev = bdl_rates[1].item_price
        bdl_rate_per = round((bdl_rate.amount - bdl_rate_prev.amount) / bdl_rate.amount * 100, 2)
        bdl_percentage_status = True if bdl_rate_per > 0 else False

        food_data = {}
        food_category = EconomicReporting.objects.filter(category_id=2).order_by('reporting_date')

        for item in food_category:
            if item.item_id not in food_data:
                food_data[item.item_id] = {}
                food_data[item.item_id] = {
                    'name': item.item.name,
                    'data': []
                }

            food_data[item.item_id]['data'].append((
                item.reporting_date.year,
                item.reporting_date.month,
                item.reporting_date.day,
                float(item.item_price.amount))
            )

        fuel_data = {}
        fuel_category = EconomicReporting.objects.filter(category_id=3).order_by('reporting_date')

        for item in fuel_category:
            if item.item_id not in fuel_data:
                fuel_data[item.item_id] = {}
                fuel_data[item.item_id] = {
                    'name': item.item.name,
                    'data': []
                }

            fuel_data[item.item_id]['data'].append((
                item.reporting_date.year,
                item.reporting_date.month,
                item.reporting_date.day,
                float(item.item_price.amount))
            )

        return {
            'official_rate': official_rate,
            'official_rate_prev': official_rate_prev,
            'official_rate_per': official_rate_per,
            'market_rate': market_rate,
            'market_rate_prev': market_rate_prev,
            'market_rate_per': market_rate_per,
            'market_percentage_status': market_percentage_status,
            'bdl_rate': bdl_rate,
            'bdl_rate_prev': bdl_rate_prev,
            'bdl_rate_per': bdl_rate_per,
            'bdl_percentage_status': bdl_percentage_status,
            'food_data': json.dumps(food_data.values()),
            'fuel_data': json.dumps(fuel_data.values()),
        }
