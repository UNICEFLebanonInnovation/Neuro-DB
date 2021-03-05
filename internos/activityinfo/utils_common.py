#!/usr/bin/env python
# coding=utf-8
# -*- coding: utf-8 -*-

import os
import csv
import datetime
import subprocess
import logging
import calendar
from datetime import date

from django.db.models import Sum, Q
from internos.activityinfo.client import Client
from internos.activityinfo.exports import get_database_data, read_file, get_xlsx
from .utils_common import *


logger = logging.getLogger(__name__)


def get_extraction_month(ai_db):

    current_year = date.today().year
    current_month = date.today().month
    reporting_year = ai_db.reporting_year.year

    if current_year - 1 >= int(reporting_year):
        return 13
    else:
        return current_month


def get_current_extraction_month(ai_db):
    current_year = date.today().year
    current_month = date.today().month
    reporting_year = ai_db.reporting_year.year

    if current_year - 1 == int(reporting_year) and current_month == 1:
        return 12
    else:
        return current_month


def get_live_extraction_month(ai_db):
    current_year = date.today().year
    current_month = date.today().month
    reporting_year = ai_db.reporting_year.year

    if current_year - 1 == int(reporting_year) and current_month == 1:
        return 12
    else:
        return current_month


def get_awp_code(name):
    try:
        if '_' in name:
            awp_code = name[:name.find('_')]
        elif ' - ' in name:
            awp_code = name[:name.find(' - ')]
            if ': ' in awp_code:
                awp_code = awp_code[:awp_code.find(': ')]
        elif ': ' in name:
            awp_code = name[:name.find(': ')]
        else:
            awp_code = name[:name.find('#')]
            if ': ' in awp_code:
                awp_code = awp_code[:awp_code.find(': ')]
    except TypeError as ex:
        awp_code = 'None'
    return awp_code


def get_label(data):
    try:
        if '------' in data['name']:
            return data['description']
    except TypeError as ex:
        pass
    return data['name']


def clean_string(value, string):
    return value.replace(string, '')

