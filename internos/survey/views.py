from __future__ import absolute_import, unicode_literals

import os
import json
import datetime
import calendar
from django.db.models import Q, Sum
from django.views.generic import ListView, TemplateView, FormView
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from datetime import date
from django.http import HttpResponseRedirect


class EconomicDashboardView(TemplateView):
    template_name = 'survey/economic_dashboard.html'

    def get_context_data(self, **kwargs):
        return {
        }
