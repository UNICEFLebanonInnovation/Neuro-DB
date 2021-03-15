#!/usr/bin/env python
# coding=utf-8
# -*- coding: utf-8 -*-

import os
import csv
import json
import datetime
import subprocess
import logging

from datetime import date
from django.db.models import Sum, Q
from django.conf import settings
from django.template.defaultfilters import length

from internos.activityinfo.models import Indicator
from internos.activityinfo.client import Client
from internos.activityinfo.exports import get_database_data, read_file, get_xlsx


logger = logging.getLogger(__name__)


def get_extraction_month(ai_db):

    current_year = date.today().year
    current_month = date.today().month
    reporting_year = ai_db.reporting_year.year

    if current_year - 1 == int(reporting_year) and current_month == 1:
        return 12
    else:
        return current_month


def r_script_command_line(ai_db):

    client = Client()
    filters = "LEFT(Month,4) == '{}'".format(ai_db.reporting_year.year)
    if ai_db.parent_id:
        get_database_data(client, database_id=ai_db.parent_id, resource_id=ai_db.db_id, database=ai_db,
                          record_filter=filters)
        get_xlsx(client, database_id=ai_db.parent_id, resource_id=ai_db.db_id, database=ai_db, record_filter=filters)
    else:
        get_database_data(client, database_id=ai_db.db_id, database=ai_db, record_filter=filters)


def read_data_from_file(ai_db, forced=False, report_type=None):
    from internos.activityinfo.models import Database, ActivityReport, LiveActivityReport
    result = 0

    if report_type == 'live':
        model = LiveActivityReport.objects.none()
        LiveActivityReport.objects.filter(database_id=ai_db.ai_id).delete()
        result = add_rows(ai_db=ai_db, model=model)

    if forced:
        model = ActivityReport.objects.none()
        ActivityReport.objects.filter(database_id=ai_db.ai_id).delete()
        result = add_rows(ai_db=ai_db, model=model)

    return result


def import_data_via_r_script(ai_db, report_type=None):
    r_script_command_line(ai_db)
    total = read_data_from_file(ai_db, True, report_type)
    return total


def clean_string(value, string):
    return value.replace(string, '')


def add_rows(ai_db=None, model=None):
    month = get_extraction_month(ai_db)
    path = os.path.dirname(os.path.abspath(__file__))
    path2file = path+'/AIReports/'+str(ai_db.ai_id)+'_ai_data.txt'
    values = read_file(path2file)
    ctr = 0

    for row in values:

        indicator_value = 0
        if 'Value' in row:
            indicator_value = row['Value']

        try:
            indicator_value = float(indicator_value)
        except Exception:
            indicator_value = 0

        funded_by = row['funded_by.funded_by'] if 'funded_by.funded_by' in row else ''
        partner_label = row['partner.name'] if 'partner.name' in row else ''
        partner_label = partner_label.replace('-', '_')
        partner_label = partner_label.encode("utf-8").replace('é', 'e')

        if partner_label == 'UNICEF':
            funded_by = 'UNICEF'

        start_date = None
        if 'month' in row and row['month'] and not row['month'] == 'NA':
            date = row['month']
            try:
                date = datetime.datetime.strptime(date, '%Y-%m-%d')
                start_date = date
            except Exception:
                start_date = '{}-01'.format(date)

        if 'month.' in row and row['month.'] and not row['month.'] == 'NA':
            start_date = '{}-01'.format(row['month.'])
        if 'date' in row and row['date'] and not row['date'] == 'NA':
            start_date = row['date']
        gov_code = 0
        gov_name = ""
        if 'governorate.code' in row:
            if row['governorate.code'] == 'NA':
                gov_code = 10
            else:
                gov_code = row['governorate.code']

        if 'governorate.name' in row:
            if row['governorate.name'] == 'NA':
                gov_name = "National"
            else:
                gov_name = row['governorate.name']

        support_covid1 = False
        support_covid2 = False
        support_covid3 = False

        if 'X4.2.3_covid_adaptation' in row:
            if row['X4.2.3_covid_adaptation'] == 'Yes':
                support_covid1 = True
            else:
                support_covid1 = False

        if 'covid_adaptation' in row:
            if row['covid_adaptation'] == 'Yes':
                support_covid2 = True
            else:
                support_covid2 = False

        if 'covid_adapted_sensitization' in row:
            if row['covid_adapted_sensitization'] == 'Yes':
                support_covid3 = True
            else:
                support_covid3 = False

        support_covid = support_covid1 or support_covid2 or support_covid3

        try:

            model.create(
                month=month,
                database=row['Folder'],
                database_id=ai_db.ai_id,
                report_id=row['FormId'],
                indicator_id=row['Quantity Field ID'],
                indicator_name=row['Quantity Field'],
                month_name=row['month'] if 'month' in row else '',
                partner_label=partner_label,
                location_adminlevel_caza_code=row['caza.code'] if 'caza.code' in row else '',
                location_adminlevel_caza=row['caza.name'] if 'caza.name' in row else '',
                form=row['Form'] if 'Form' in row else '',
                location_adminlevel_cadastral_area_code=row[
                    'cadastral_area.code'] if 'cadastral_area.code' in row else '',
                location_adminlevel_cadastral_area=row['cadastral_area.name'] if 'cadastral_area.name' in row else '',
                governorate=row['governorate'] if 'governorate' in row else '',
                location_adminlevel_governorate_code=gov_code,
                location_adminlevel_governorate=gov_name,
                partner_description=row['partner.partner_full_name'] if 'partner.partner_full_name' in row else '',
                project_start_date=row['projects.start_date'] if 'projects.start_date' in row and not row['projects.start_date'] == 'NA' else None,
                project_end_date=row['projects.end_date'] if 'projects.end_date' in row and not row['projects.start_date'] == 'NA' else None,
                project_label=row['projects.project_code'] if 'projects.project_code' in row else '',
                project_description=row['projects.project_name'] if 'projects.project_name' in row else '',
                funded_by=funded_by,
                indicator_value=indicator_value,
                indicator_units=row['units'] if 'units' in row else '',
                reporting_section=row['reporting_section'] if 'reporting_section' in row else '',
                site_type=row['site_type'] if 'site_type' in row else '',
                location_longitude=row[
                    'ai_allsites.geographic_location.longitude'] if 'ai_allsites.geographic_location.longitude' in row else '',
                location_latitude=row[
                    'ai_allsites.geographic_location.latitude'] if 'ai_allsites.geographic_location.latitude' in row else '',
                location_alternate_name=row[
                    'ai_allsites.alternate_name'] if 'ai_allsites.alternate_name' in row else '',

                location_name=row['ai_allsites.name'] if 'ai_allsites.name' in row else '',
                partner_id=row['partner_id'] if 'partner_id' in row else partner_label,
                support_covid=support_covid,
                start_date=start_date,
            )
            ctr += 1
        except Exception as ex:
            print(ex)

    return ctr


def link_indicators_data(ai_db, report_type=None):
    result = link_indicators_activity_report(ai_db, report_type)

    return result


def link_indicators_activity_report(ai_db, report_type=None):
    from internos.activityinfo.models import Indicator, ActivityReport, LiveActivityReport

    ctr = 0
    if report_type == 'live':
        reports = LiveActivityReport.objects.filter(database_id=ai_db.ai_id)
    else:
        reports = ActivityReport.objects.filter(database_id=ai_db.ai_id)

    reports = reports.exclude(ai_indicator__isnull=False)

    # if ai_db.is_funded_by_unicef:
    #     reports = reports.filter(funded_by='UNICEF')

    indicators = Indicator.objects.filter(
        activity__database__ai_id=ai_db.ai_id).exclude(
        master_indicator=True).exclude(master_indicator_sub=True)

    for item in indicators:
        if not item.ai_indicator:
            continue
        ai_values = reports.filter(indicator_id=item.ai_indicator)
        if not ai_values.count():
            continue
        ctr += ai_values.count()
        print(ai_values)
        ai_values.update(ai_indicator_id=item.id)

    return ctr


def reset_indicators_values(ai_id, report_type=None):
    from internos.activityinfo.models import Indicator

    indicators = Indicator.objects.filter(activity__database__ai_id=ai_id)

    for indicator in indicators:
        if report_type == 'live':
            indicator.values_crisis_live = {}
            indicator.values_crisis_gov_live = {}
            indicator.values_crisis_partners_live = {}
            indicator.values_crisis_partners_gov_live = {}
            indicator.values_sections_live = {}
            indicator.values_sections_partners_live = {}
            indicator.values_sections_gov_live = {}
            indicator.values_sections_partners_gov_live = {}
            indicator.values_crisis_cumulative_live = {}
        elif report_type == 'weekly':
            indicator.values_weekly = {}
            indicator.values_gov_weekly = {}
            indicator.values_partners_weekly = {}
            indicator.values_partners_gov_weekly = {}
            indicator.values_cumulative_weekly = {}
            indicator.values_sections = {}
            indicator.values_sections_partners = {}
            indicator.values_sections_gov = {}
            indicator.values_sections_partners_gov = {}
        indicator.save()

    return indicators.count()


def calculate_indicators_values(ai_db, report_type=None):
    print('reset_indicators_values')
    reset_indicators_values(ai_db.ai_id, report_type)
    print('calculate_individual_indicators_values_2')
    if report_type == 'live':
        calculate_individual_indicators_values_2(ai_db)
        calculate_individual_indicators_live_imported_values(ai_db)
    elif report_type == 'weekly':
        calculate_individual_indicators_weekly_values(ai_db)
        calculate_individual_indicators_weekly_imported_values(ai_db)

    print('calculate_master_indicators_values_1')
    calculate_master_indicators_values_1(ai_db, report_type, True)
    print('calculate_master_indicators_values_1')
    calculate_master_indicators_values_1(ai_db, report_type)
    print('calculate_master_indicators_values_percentage')
    calculate_master_indicators_values_percentage(ai_db, report_type)
    print('calculate_master_indicators_values_denominator_multiplication')
    calculate_master_indicators_values_denominator_multiplication(ai_db, report_type)
    print('calculate_indicators_values_percentage_1')
    calculate_indicators_values_percentage_1(ai_db, report_type)  # DONE
    print('calculate_master_imported_indicators')
    calculate_master_imported_indicators(ai_db,report_type)
    print('calculate_indicators_cumulative_results_1')
    calculate_indicators_cumulative_results_1(ai_db, report_type)
    # print('calculate_indicators_status')
    # calculate_indicators_status(ai_db)
    if report_type == 'weekly':
        print('calculate_indicators_all_tags_weekly')
        calculate_indicators_all_tags_weekly(ai_db)

    return 0


def calculate_individual_indicators_weekly_values(ai_db):
    from django.db import connection
    from internos.activityinfo.models import Indicator

    ai_id = str(ai_db.ai_id)
    # current_month = int(datetime.datetime.now().strftime("%m")) + 1
    current_month = get_extraction_month(ai_db) + 1

    indicators = Indicator.objects.filter(activity__database__ai_id=ai_db.ai_id).exclude(master_indicator=True) \
        .exclude(master_indicator_sub=True).only(
        'ai_indicator',
        'values_weekly',
        'values_gov_weekly',
        'values_partners_weekly',
        'values_partners_gov_weekly',
        'values_sections',
        'values_sections_partners',
        'values_sections_gov',
        'values_sections_partners_gov',
    )

    rows_months = {}
    rows_partners = {}
    rows_govs = {}
    rows_partners_govs = {}
    rows_sections = {}
    rows_sections_partners = {}
    rows_sections_gov = {}
    rows_sections_partners_gov = {}
    cursor = connection.cursor()

    covid_condition = ""

    if ai_db.support_covid:
        covid_condition = "AND support_covid = true "

    funded_condition = ""

    if ai_db.is_funded_by_unicef:
        funded_condition = "AND funded_by = 'UNICEF' "

    query_condition = " WHERE date_part('month', start_date) = %s AND database_id = %s " + funded_condition + covid_condition

    for month in range(1, current_month):
        month = str(month)
        cursor.execute("SELECT indicator_id, SUM(indicator_value) as indicator_value "
                       "FROM activityinfo_activityreport "
                       + query_condition +
                       " GROUP BY indicator_id", [month, ai_id])
        rows = cursor.fetchall()

        for row in rows:
            if row[0] not in rows_months:
                rows_months[row[0]] = {}
            rows_months[row[0]][month] = row[1]

        cursor.execute(
            "SELECT indicator_id, SUM(indicator_value) as indicator_value, location_adminlevel_governorate_code"
            " FROM activityinfo_activityreport "
            + query_condition +
            "GROUP BY indicator_id, location_adminlevel_governorate_code", [month, ai_id])

        rows = cursor.fetchall()

        for row in rows:
            if row[0] not in rows_govs:
                rows_govs[row[0]] = {}
            key = "{}-{}".format(month, row[2])
            rows_govs[row[0]][key] = row[1]

        cursor.execute(
            "SELECT indicator_id, SUM(indicator_value) as indicator_value, partner_id "
            "FROM activityinfo_activityreport "
            + query_condition +
            "GROUP BY indicator_id, partner_id",
            [month, ai_id])

        rows = cursor.fetchall()

        for row in rows:
            if row[0] not in rows_partners:
                rows_partners[row[0]] = {}
            key = "{}-{}".format(month, row[2])
            rows_partners[row[0]][key] = row[1]

        cursor.execute(
            "SELECT indicator_id, SUM(indicator_value) as indicator_value, location_adminlevel_governorate_code, partner_id "
            "FROM activityinfo_activityreport "
            + query_condition +
            "GROUP BY indicator_id, location_adminlevel_governorate_code, partner_id",
            [month, ai_id])

        rows = cursor.fetchall()

        for row in rows:
            if row[0] not in rows_partners_govs:
                rows_partners_govs[row[0]] = {}
            key = "{}-{}-{}".format(month, row[2], row[3])
            rows_partners_govs[row[0]][key] = row[1]


        cursor.execute(
            "SELECT indicator_id, SUM(indicator_value) as indicator_value, reporting_section "
            "FROM activityinfo_activityreport "
            + query_condition +
            "GROUP BY indicator_id, reporting_section",
            [month, ai_id])


        rows = cursor.fetchall()
        for row in rows:
            if row[0] not in rows_sections:
                rows_sections[row[0]] = {}
            key = "{}-{}".format(month, row[2])
            rows_sections[row[0]][key] = row[1]

        cursor.execute(
            "SELECT indicator_id, SUM(indicator_value) as indicator_value, reporting_section ,partner_id "
            "FROM activityinfo_activityreport "
            + query_condition +
            "GROUP BY indicator_id, reporting_section ,partner_id",
            [month, ai_id])

        rows = cursor.fetchall()
        for row in rows:
            if row[0] not in rows_sections_partners:
                rows_sections_partners[row[0]] = {}
            key = "{}-{}-{}".format(month, row[2], row[3])
            rows_sections_partners[row[0]][key] = row[1]

        cursor.execute(
            "SELECT indicator_id, SUM(indicator_value) as indicator_value, reporting_section, "
            "location_adminlevel_governorate_code "
            "FROM activityinfo_activityreport "
            + query_condition +
            "GROUP BY indicator_id, reporting_section ,location_adminlevel_governorate_code",
            [month, ai_id])

        rows = cursor.fetchall()
        for row in rows:
            if row[0] not in rows_sections_gov:
                rows_sections_gov[row[0]] = {}
            key = "{}-{}-{}".format(month, row[2], row[3])
            rows_sections_gov[row[0]][key] = row[1]

        cursor.execute(
            "SELECT indicator_id, SUM(indicator_value) as indicator_value, reporting_section, "
            "location_adminlevel_governorate_code, partner_id "
            "FROM activityinfo_activityreport "
            + query_condition +
            "GROUP BY indicator_id, reporting_section , partner_id ,location_adminlevel_governorate_code",
            [month, ai_id])

        rows = cursor.fetchall()
        for row in rows:
            if row[0] not in rows_sections_partners_gov:
                rows_sections_partners_gov[row[0]] = {}
            key = "{}-{}-{}-{}".format(month, row[2], row[3], row[4])
            rows_sections_partners_gov[row[0]][key] = row[1]

    for indicator in indicators.iterator():
        if indicator.ai_indicator in rows_months:
            indicator.values_weekly = rows_months[indicator.ai_indicator]

        if indicator.ai_indicator in rows_partners:
            indicator.values_partners_weekly = rows_partners[indicator.ai_indicator]

        if indicator.ai_indicator in rows_govs:
            indicator.values_gov_weekly = rows_govs[indicator.ai_indicator]

        if indicator.ai_indicator in rows_partners_govs:
            indicator.values_partners_gov_weekly = rows_partners_govs[indicator.ai_indicator]

        if indicator.ai_indicator in rows_sections:
            indicator.values_sections = rows_sections[indicator.ai_indicator]

        if indicator.ai_indicator in rows_sections_gov:
            indicator.values_sections_gov = rows_sections_gov[indicator.ai_indicator]

        if indicator.ai_indicator in rows_sections_partners:
            indicator.values_sections_partners = rows_sections_partners[indicator.ai_indicator]

        if indicator.ai_indicator in rows_sections_partners_gov:
            indicator.values_sections_partners_gov = rows_sections_partners_gov[indicator.ai_indicator]

        indicator.save()


def calculate_individual_indicators_weekly_imported_values(ai_db):
    from django.db import connection
    from internos.activityinfo.models import Indicator

    ai_id = str(ai_db.ai_id)
    # current_month = int(datetime.datetime.now().strftime("%m")) + 1
    current_month = get_extraction_month(ai_db) + 1
    master_indicators = Indicator.objects.filter(activity__database__ai_id=ai_db.ai_id,is_imported_by_calculation=True)
    if master_indicators:
        linked_indicators=[]

        for master_ind in master_indicators:

            indicators = Indicator.objects.filter(summation_sub_indicators=master_ind.id).only(
            'ai_indicator',
            'values_weekly',
            'values_gov_weekly',
            'values_partners_weekly',
            'values_partners_gov_weekly',
            )
            indicators =list(indicators)
            for ind in indicators:
                linked_indicators.append(ind)
        indicators_ids=[]

        for ind in linked_indicators:
            value = ind.ai_indicator
            indicators_ids.append(value)

        ids_condition =','.join(("'{}'".format(str(n)) for n in indicators_ids))

        rows_months = {}
        rows_partners = {}
        rows_govs = {}
        rows_partners_govs = {}

        cursor = connection.cursor()

        if ai_db.support_covid:

            funded_condition = ""

            if ai_db.is_funded_by_unicef:
                funded_condition = "AND funded_by = 'UNICEF' "

            query_condition = " WHERE date_part('month', start_date) = %s AND database_id = %s " + funded_condition + " and indicator_id in (" + ids_condition +")"

            for month in range(4, current_month):
                month = str(month)
                cursor.execute("SELECT indicator_id, SUM(indicator_value) as indicator_value "
                           "FROM activityinfo_activityreport "
                           + query_condition +
                           " GROUP BY indicator_id", [month, ai_id])
                rows = cursor.fetchall()

                for row in rows:
                    if row[0] not in rows_months:
                        rows_months[row[0]] = {}
                    rows_months[row[0]][month] = row[1]

                cursor.execute(
                    "SELECT indicator_id, SUM(indicator_value) as indicator_value, location_adminlevel_governorate_code"
                    " FROM activityinfo_activityreport "
                    + query_condition +
                    "GROUP BY indicator_id, location_adminlevel_governorate_code", [month, ai_id])

                rows = cursor.fetchall()

                for row in rows:
                    if row[0] not in rows_govs:
                        rows_govs[row[0]] = {}
                    key = "{}-{}".format(month, row[2])
                    rows_govs[row[0]][key] = row[1]

                cursor.execute(
                    "SELECT indicator_id, SUM(indicator_value) as indicator_value, partner_id "
                    "FROM activityinfo_activityreport "
                    + query_condition +
                    "GROUP BY indicator_id, partner_id",
                    [month, ai_id])

                rows = cursor.fetchall()

                for row in rows:
                    if row[0] not in rows_partners:
                        rows_partners[row[0]] = {}
                    key = "{}-{}".format(month, row[2])
                    rows_partners[row[0]][key] = row[1]

                cursor.execute(
                    "SELECT indicator_id, SUM(indicator_value) as indicator_value, location_adminlevel_governorate_code, partner_id "
                    "FROM activityinfo_activityreport "
                    + query_condition +
                    "GROUP BY indicator_id, location_adminlevel_governorate_code, partner_id",
                    [month, ai_id])

                rows = cursor.fetchall()

                for row in rows:
                    if row[0] not in rows_partners_govs:
                        rows_partners_govs[row[0]] = {}
                    key = "{}-{}-{}".format(month, row[2], row[3])
                    rows_partners_govs[row[0]][key] = row[1]

            for indicator in linked_indicators:
                if indicator.ai_indicator in rows_months:
                    indicator.values_weekly = rows_months[indicator.ai_indicator]

                if indicator.ai_indicator in rows_partners:
                    indicator.values_partners_weekly = rows_partners[indicator.ai_indicator]

                if indicator.ai_indicator in rows_govs:
                    indicator.values_gov_weekly = rows_govs[indicator.ai_indicator]

                if indicator.ai_indicator in rows_partners_govs:
                    indicator.values_partners_gov_weekly = rows_partners_govs[indicator.ai_indicator]

                indicator.save()


def calculate_individual_indicators_live_imported_values(ai_db):
    from django.db import connection
    from internos.activityinfo.models import Indicator

    ai_id = str(ai_db.ai_id)
    # current_month = int(datetime.datetime.now().strftime("%m")) + 1
    current_month = get_extraction_month(ai_db) + 1
    master_indicators = Indicator.objects.filter(activity__database__ai_id=ai_db.ai_id,
                                                 is_imported_by_calculation=True)
    if master_indicators:
        linked_indicators = []

        for master_ind in master_indicators:

            indicators = Indicator.objects.filter(summation_sub_indicators=master_ind.id).only(
                'ai_indicator',
                'values_crisis_live',
                'values_crisis_gov_live',
                'values_crisis_partners_live',
                'values_crisis_partners_gov_live',
            )
            indicators = list(indicators)
            for ind in indicators:
                linked_indicators.append(ind)
        indicators_ids = []

        for ind in linked_indicators:
            value = ind.ai_indicator
            indicators_ids.append(value)

        ids_condition = ','.join(("'{}'".format(str(n)) for n in indicators_ids))

        rows_months = {}
        rows_partners = {}
        rows_govs = {}
        rows_partners_govs = {}

        cursor = connection.cursor()

        if ai_db.support_covid:

            funded_condition = ""

            if ai_db.is_funded_by_unicef:
                funded_condition = "AND funded_by = 'UNICEF' "

            query_condition = " WHERE date_part('month', start_date) = %s AND database_id = %s " + funded_condition + " and indicator_id in (" + ids_condition + ")"

            for month in range(4, current_month):
                month = str(month)
                cursor.execute("SELECT indicator_id, SUM(indicator_value) as indicator_value "
                               "FROM activityinfo_liveactivityreport "
                               + query_condition +
                               " GROUP BY indicator_id", [month, ai_id])
                rows = cursor.fetchall()

                for row in rows:
                    if row[0] not in rows_months:
                        rows_months[row[0]] = {}
                    rows_months[row[0]][month] = row[1]

                cursor.execute(
                    "SELECT indicator_id, SUM(indicator_value) as indicator_value, location_adminlevel_governorate_code"
                    " FROM activityinfo_liveactivityreport "
                    + query_condition +
                    "GROUP BY indicator_id, location_adminlevel_governorate_code", [month, ai_id])

                rows = cursor.fetchall()

                for row in rows:
                    if row[0] not in rows_govs:
                        rows_govs[row[0]] = {}
                    key = "{}-{}".format(month, row[2])
                    rows_govs[row[0]][key] = row[1]

                cursor.execute(
                    "SELECT indicator_id, SUM(indicator_value) as indicator_value, partner_id "
                    "FROM activityinfo_liveactivityreport "
                    + query_condition +
                    "GROUP BY indicator_id, partner_id",
                    [month, ai_id])

                rows = cursor.fetchall()

                for row in rows:
                    if row[0] not in rows_partners:
                        rows_partners[row[0]] = {}
                    key = "{}-{}".format(month, row[2])
                    rows_partners[row[0]][key] = row[1]

                cursor.execute(
                    "SELECT indicator_id, SUM(indicator_value) as indicator_value, location_adminlevel_governorate_code, partner_id "
                    "FROM activityinfo_liveactivityreport "
                    + query_condition +
                    "GROUP BY indicator_id, location_adminlevel_governorate_code, partner_id",
                    [month, ai_id])

                rows = cursor.fetchall()

                for row in rows:
                    if row[0] not in rows_partners_govs:
                        rows_partners_govs[row[0]] = {}
                    key = "{}-{}-{}".format(month, row[2], row[3])
                    rows_partners_govs[row[0]][key] = row[1]

            for indicator in linked_indicators:
                if indicator.ai_indicator in rows_months:
                    indicator.values_crisis_live = rows_months[indicator.ai_indicator]

                if indicator.ai_indicator in rows_partners:
                    indicator.values_crisis_partners_live = rows_partners[indicator.ai_indicator]

                if indicator.ai_indicator in rows_govs:
                    indicator.values_crisis_gov_live = rows_govs[indicator.ai_indicator]

                if indicator.ai_indicator in rows_partners_govs:
                    indicator.values_crisis_partners_gov_live = rows_partners_govs[indicator.ai_indicator]

                indicator.save()


def calculate_indicators_cumulative_results_1(ai_db, report_type=None):
    from django.db import connection
    from internos.activityinfo.models import Indicator

    indicators = Indicator.objects.filter(activity__database__ai_id=ai_db.ai_id).only(
        'id',
        'values_weekly',
        'values_gov_weekly',
        'values_partners_weekly',
        'values_partners_gov_weekly',
        'values_cumulative_weekly',
        'values_crisis_live',
        'values_crisis_gov_live',
        'values_crisis_partners_live',
        'values_crisis_partners_gov_live',
        'values_cumulative_weekly',
        'values_crisis_cumulative_live',
        'values_sections',
        'values_sections_partners',
        'values_sections_gov',
        'values_sections_partners_gov',
        'values_sections_live',
        'values_sections_partners_live',
        'values_sections_gov_live',
        'values_sections_partners_gov_live',

    )

    rows_data = {}
    cursor = connection.cursor()
    cursor.execute(
        "SELECT distinct ai.id, ai.ai_indicator,aa.id, aa.name, ai.values_weekly, ai.values_crisis_live, "
        "ai.values_gov_weekly, ai.values_crisis_gov_live, ai.values_partners_weekly,"
        " ai.values_crisis_partners_live, "
        "ai.values_partners_gov_weekly, ai.values_crisis_partners_gov_live , "
        "ai.values_sections, ai.values_sections_live, "
        "ai.values_sections_partners, ai.values_sections_partners_live, ai.values_sections_gov, "
        "ai.values_sections_gov_live, ai.values_sections_partners_gov, "
        "ai.values_sections_partners_gov_live "
        "  FROM public.activityinfo_indicator ai, public.activityinfo_activity aa "
        "WHERE ai.activity_id = aa.id AND aa.database_id = %s",
        [ai_db.id])

    rows = cursor.fetchall()
    for row in rows:
        rows_data[row[0]] = row

    for indicator in indicators.iterator():
        values_month = {}
        values_partners = {}
        values_gov = {}
        values_partners_gov = {}
        values_sections = {}
        values_sections_partners = {}
        values_sections_gov = {}
        values_sections_partners_gov = {}

        if indicator.id in rows_data:

            indicator_values = rows_data[indicator.id]

            if report_type == 'live':
                values = indicator_values[5]  # values_live
                values1 = indicator_values[7]  # values_gov_live
                values2 = indicator_values[9]  # values_partners_live
                values3 = indicator_values[11]  # values_partners_gov_live
                values4 = indicator_values[13]  # values_sections_live
                values5 = indicator_values[15]  # values_sections_partners_live
                values6 = indicator_values[17]  # values_sections_gov_live
                values7 = indicator_values[19]  # values_sections_partners_gov_live

            elif report_type == 'weekly':
                values = indicator_values[4]  # values
                values1 = indicator_values[6]  # values_gov
                values2 = indicator_values[8]  # values_partners
                values3 = indicator_values[10]  # values_partners_gov
                values4 = indicator_values[12]  # values_sections
                values5 = indicator_values[14]  # values_sections_partners
                values6 = indicator_values[16]  # values_sections_gov
                values7 = indicator_values[18]  # values_sections_partners_gov

            c_value = 0
            for key, value in values.items():
                c_value += value
                values_month = c_value

            for key, value in values1.items():

                keys = key.split('-')
                gov = keys[1]
                if gov in values_gov:
                    values_gov[gov] = values_gov[gov] + value
                else:
                    values_gov[gov] = value

            for key, value in values2.items():
                keys = key.split('-')
                partner = keys[1]
                if partner in values_partners:
                    values_partners[partner] = values_partners[partner] + value
                else:
                    values_partners[partner] = value

            for key, value in values3.items():
                keys = key.split('-')
                gov_partner = '{}-{}'.format(keys[1], keys[2])
                if gov_partner in values_partners_gov:
                    values_partners_gov[gov_partner] = values_partners_gov[gov_partner] + value
                else:
                    values_partners_gov[gov_partner] = value

            if values4:
                for key, value in values4.items():
                    keys = key.split('-')
                    if len(keys) == 2:
                        section = keys[1]
                        if section in values_sections:
                            values_sections[section] = values_sections[section] + value
                        else:
                            values_sections[section] = value

            if values5:
                for key, value in values5.items():
                    keys = key.split('-')
                    if len(keys) == 3:
                        section_partner = '{}-{}'.format(keys[1], keys[2])
                        if section_partner in values_sections_partners:
                            values_sections_partners[section_partner] = values_sections_partners[section_partner] + value
                        else:
                            values_sections_partners[section_partner] = value

            if values6:
                for key, value in values6.items():
                    keys = key.split('-')
                    if len(keys) == 3:
                        section_gov = '{}-{}'.format(keys[1], keys[2])
                        if section_gov in values_sections_gov:
                            values_sections_gov[section_gov] = values_sections_gov[section_gov] + value
                        else:
                            values_sections_gov[section_gov] = value

            if values7:
                for key, value in values7.items():
                    keys = key.split('-')
                    if len(keys) == 4:
                        section_partner_gov = '{}-{}-{}'.format(keys[1], keys[2], keys[3])
                        if section_partner_gov in values_sections_partners_gov:
                            values_sections_partners_gov[section_partner_gov] = values_sections_partners_gov[
                                                                                        section_partner_gov] + value
                        else:
                            values_sections_partners_gov[section_partner_gov] = value

            if report_type == 'live':
                indicator.values_crisis_cumulative_live = {
                    'months': values_month,
                    'partners': values_partners,
                    'govs': values_gov,
                    'partners_govs': values_partners_gov,
                    'sections': values_sections,
                    'sections_partners': values_sections_partners,
                    'sections_gov': values_sections_gov,
                    'sections_partners_gov': values_sections_partners_gov
                }
            elif report_type == 'weekly':
                indicator.values_cumulative_weekly = {
                    'months': values_month,
                    'partners': values_partners,
                    'govs': values_gov,
                    'partners_govs': values_partners_gov,
                    'sections': values_sections,
                    'sections_partners': values_sections_partners,
                    'sections_gov': values_sections_gov,
                    'sections_partners_gov': values_sections_partners_gov
                }

            indicator.save()

    return indicators.count()


def calculate_indicators_cumulative_results(ai_db, report_type=None):
    from internos.activityinfo.models import Indicator, ActivityReport, LiveActivityReport

    indicators = Indicator.objects.filter(activity__database__ai_id=ai_db.ai_id)

    if report_type == 'live':
        report = LiveActivityReport.objects.filter(database=ai_db)
    else:
        report = ActivityReport.objects.filter(database=ai_db)

    if ai_db.is_funded_by_unicef:
        report = report.filter(funded_by__contains='UNICEF')

    partners = report.values('partner_id').order_by('partner_id').distinct('partner_id')
    governorates = report.values('location_adminlevel_governorate_code').order_by(
        'location_adminlevel_governorate_code').distinct('location_adminlevel_governorate_code')

    for indicator in indicators:
        value = 0
        cum_month = {}
        cum_partner = {}
        cum_gov = {}
        cum_partner_gov = {}

        if report_type == 'live':
            values = indicator.values_live
            values_partners = indicator.values_partners_live
            values_govs = indicator.values_gov_live
            values_partners_govs = indicator.values_partners_gov_live
        else:
            values = indicator.values
            values_partners = indicator.values_partners
            values_govs = indicator.values_gov
            values_partners_govs = indicator.values_partners_gov

        for month in values:
            c_value = 0
            for c_month in range(1, int(month) + 1):
                c_value = 0
                if c_month in values:
                    c_value += float(values[str(c_month)])
                cum_month[str(month)] = c_value

            for partner in partners:
                key = '{}-{}'.format(month, partner['partner_id'])
                if key in values_partners:
                    cum_partner[partner['partner_id']] = values_partners[key] + (
                        cum_partner[partner['partner_id']] if partner['partner_id'] in cum_partner else 0)

            for gov in governorates:
                key = '{}-{}'.format(month, gov['location_adminlevel_governorate_code'])
                if key in values_govs:
                    cum_gov[gov['location_adminlevel_governorate_code']] = values_govs[key] + (
                        cum_gov[gov['location_adminlevel_governorate_code']] if gov[
                                                                                    'location_adminlevel_governorate_code'] in cum_gov else 0)

                for partner in partners:
                    key = '{}-{}-{}'.format(month, partner['partner_id'], gov['location_adminlevel_governorate_code'])
                    key_c = '{}-{}'.format(partner['partner_id'], gov['location_adminlevel_governorate_code'])
                    if key in values_partners_govs:
                        cum_partner_gov[key_c] = values_partners_govs[key] + (
                            cum_partner_gov[key_c] if key_c in cum_partner_gov else 0)

        if report_type == 'live':
            indicator.cumulative_values_live = {
                'months': cum_month,
                'partners': cum_partner,
                'govs': cum_gov,
                'partners_govs': cum_partner_gov
            }
        else:
            indicator.cumulative_values = {
                'months': cum_month,
                'partners': cum_partner,
                'govs': cum_gov,
                'partners_govs': cum_partner_gov
            }
        indicator.save()

    return indicators.count()


def calculate_indicators_all_tags_weekly(ai_db):

    calculate_indicators_tags_weekly(ai_db, False)
    calculate_indicators_tags_weekly(ai_db,True)



def calculate_indicators_tags_weekly(ai_db,sub_master=False):
    from internos.activityinfo.models import Indicator, IndicatorTag, ActivityReport

    if sub_master:
        indicators = Indicator.objects.filter(activity__database__ai_id=ai_db.ai_id). \
            filter(Q(master_indicator_sub=True))
    else:
        indicators = Indicator.objects.filter(activity__database__ai_id=ai_db.ai_id).filter(
            Q(master_indicator=True) | Q(hpm_indicator=True))

    # report = ActivityReport.objects.filter(database_id=ai_db.ai_id)
    #
    # if ai_db.is_funded_by_unicef:
    #     report = report.filter(funded_by__contains='UNICEF')

    # partners = report.values('partner_id').order_by('partner_id').distinct('partner_id')
    # governorates = report.values('location_adminlevel_governorate_code').distinct()
    # sections = report.values('reporting_section').distinct()

    partners = get_partners_list(ai_db)
    governorates = get_governorates_list(ai_db)
    sections= get_reporting_sections_list(ai_db)

    tags_gender = IndicatorTag.objects.filter(type='gender').only('id', 'name')
    tags_age = IndicatorTag.objects.filter(type='age').only('id', 'name')
    tags_nationality = IndicatorTag.objects.filter(type='nationality').only('id', 'name')
    tags_disability = IndicatorTag.objects.filter(type='disability').only('id', 'name')
    tags_programme = IndicatorTag.objects.filter(type='programme').only('id', 'name')

    for indicator in indicators.iterator():
        indicator.values_tags_weekly = {}
        indicator.save()

    for indicator in indicators.iterator():

        sub_indicators = indicator.summation_sub_indicators.all()
        for sub_indicator in sub_indicators:
            if sub_indicator.master_indicator and not sub_indicator.is_imported:
                continue
            else:
                sub_indicators = sub_indicators | sub_indicator.summation_sub_indicators.all()

        sub_indicators = sub_indicators.only(
            'values_sections',
            'values_sections_partners',
            'values_sections_gov',
            'values_tags_weekly',
            'values_weekly',
            'values_gov_weekly',
            'values_partners_weekly',
            'values_partners_gov_weekly',
            'values_cumulative_weekly'
        ).distinct()


        # ----------------------------- Gender tags --------------------------------
        for tag in tags_gender.iterator():
            tag_sub_indicators = sub_indicators.filter(tag_gender_id=tag.id)
            if tag_sub_indicators:

                # -----------------------------  tags calculations per month  --------------------------------
                months_list = {}
                for mon in range(1, 13):
                    mon_value = 0
                    for ind_tag in tag_sub_indicators:
                        if str(mon) in ind_tag.values_weekly:
                            mon_value += ind_tag.values_weekly[str(mon)]
                            months_list['{}--{}'.format(mon, tag.name)] = mon_value
                indicator.values_tags_weekly['months_' + tag.name] = months_list

                # -----------------------------  tags calculations per partner  --------------------------------
                partners_list = {}
                for mon in range(1, 13):
                    for par in partners:
                        par = par['partner_id']
                        par_value = 0
                        for ind_tag in tag_sub_indicators:
                            key = '{}-{}'.format(mon, par)
                            if key in ind_tag.values_partners_weekly:
                                par_value += ind_tag.values_partners_weekly[key]
                                partners_list['{}--{}--{}'.format(mon, par, tag.name)] = par_value
                indicator.values_tags_weekly['partners_' + tag.name] = partners_list

                # -----------------------------  tags calculations per governorate  --------------------------------
                govs_list = {}
                for mon in range(1, 13):
                    for gov in governorates:
                        gov = gov['location_adminlevel_governorate_code']
                        gov_value = 0
                        for ind_tag in tag_sub_indicators:
                            key = '{}-{}'.format(mon, gov)
                            if key in ind_tag.values_gov_weekly:
                                gov_value += ind_tag.values_gov_weekly[key]
                                govs_list['{}--{}--{}'.format(mon, gov, tag.name)] = gov_value

                indicator.values_tags_weekly['govs_' + tag.name] = govs_list

                # -----------------------------  tags calculations per sections  --------------------------------
                sections_list = {}
                for mon in range(1, 13):
                    for sec in sections:
                        sec = sec['reporting_section']
                        sec_value = 0
                        for ind_tag in tag_sub_indicators:
                            key = '{}-{}'.format(mon, sec)
                            if ind_tag.values_sections:
                                if key in ind_tag.values_sections:
                                    sec_value += ind_tag.values_sections[key]
                                    sections_list['{}--{}--{}'.format(mon, sec, tag.name)] = sec_value

                indicator.values_tags_weekly['sections_' + tag.name] = sections_list

                # -----------------------------  tags calculations per partner per gov --------------------------------
                partner_gov_list = {}
                for mon in range(1, 13):
                    for par in partners:
                        par = par['partner_id']
                        for gov in governorates:
                            gov = gov['location_adminlevel_governorate_code']
                            par_gv_value = 0
                            for ind_tag in tag_sub_indicators:
                                key = '{}-{}-{}'.format(mon, gov, par)
                                if key in ind_tag.values_partners_gov_weekly:
                                    par_gv_value += ind_tag.values_partners_gov_weekly[key]
                                    partner_gov_list['{}--{}--{}--{}'.format(mon, par, gov, tag.name)] = par_gv_value
                indicator.values_tags_weekly['partners_govs_' + tag.name] = partner_gov_list

                # ---------------------------  tags calculations per partner per section  ----------------------------
                partner_sec_list = {}
                for mon in range(1, 13):
                    for par in partners:
                        par = par['partner_id']
                        for sec in sections:
                            sec = sec['reporting_section']
                            par_sec_value = 0
                            for ind_tag in tag_sub_indicators:
                                if ind_tag.values_sections_partners:
                                    key = '{}-{}-{}'.format(mon, sec, par)
                                    if key in ind_tag.values_sections_partners:
                                        par_sec_value += ind_tag.values_sections_partners[key]
                                        partner_sec_list['{}--{}--{}--{}'.format(mon, par, sec, tag.name)] = par_sec_value
                indicator.values_tags_weekly['partners_sections_' + tag.name] = partner_sec_list

                # -------------------  tags calculations per gov per section  --------------------------------

                gov_sec_list = {}
                for mon in range(1, 13):
                    for gov in governorates:
                        gov = gov['location_adminlevel_governorate_code']
                        for sec in sections:
                            sec = sec['reporting_section']
                            gov_sec_value = 0
                            for ind_tag in tag_sub_indicators:
                                key = '{}-{}-{}'.format(mon, sec, gov)
                                if  ind_tag.values_sections_gov:
                                    if key in ind_tag.values_sections_gov:
                                        gov_sec_value += ind_tag.values_sections_gov[key]
                                        gov_sec_list['{}--{}--{}--{}'.format(mon, gov, sec, tag.name)] = gov_sec_value
                indicator.values_tags_weekly['govs_sections_' + tag.name] = gov_sec_list

                # ----------------- tags calculations per gov per section per partner -----------------------

                partner_gov_sec_list = {}
                for mon in range(1, 13):
                    for sec in sections:
                        sec = sec['reporting_section']
                        for par in partners:
                            par = par['partner_id']
                            for gov in governorates:
                                gov = gov['location_adminlevel_governorate_code']
                                partner_gov_sec_value = 0
                                for ind_tag in tag_sub_indicators:
                                    key = '{}-{}-{}-{}'.format(mon, sec, par, gov)
                                    if ind_tag.values_sections_partners_gov:
                                        if key in ind_tag.values_sections_partners_gov:
                                            partner_gov_sec_value += ind_tag.values_sections_partners_gov[key]
                                            partner_gov_sec_list['{}--{}--{}--{}--{}'.format(mon, par, gov, sec,
                                                                                             tag.name)] = partner_gov_sec_value
                indicator.values_tags_weekly['partners_govs_sections_' + tag.name] = partner_gov_sec_list

                # --------------- tags cumulative calculations per gov per partner   ---------------------

                cum_partner_gov = {}

                for gov in governorates:
                    gov = gov['location_adminlevel_governorate_code']
                    for par in partners:
                        par = par['partner_id']
                        par_gv_cum_value = 0
                        for ind_tag in tag_sub_indicators:
                            key = '{}-{}'.format(gov, par)
                            if 'partners_govs' in ind_tag.values_cumulative_weekly:
                                if key in ind_tag.values_cumulative_weekly['partners_govs']:
                                    par_gv_cum_value += ind_tag.values_cumulative_weekly['partners_govs'][key]
                                    cum_partner_gov['{}--{}--{}'.format(par, gov, tag.name)] = par_gv_cum_value
                indicator.values_tags_weekly['cum_partner_gov_' + tag.name] = cum_partner_gov

                # ----------------- tags cumulative calculations per section per partner   ---------------------

                cum_partner_section = {}

                for sec in sections:
                    sec = sec['reporting_section']
                    for par in partners:
                        par = par['partner_id']
                        par_sec_cum_value = 0
                        for ind_tag in tag_sub_indicators:
                            key = '{}-{}'.format(sec, par)
                            if 'sections_partners' in ind_tag.values_cumulative_weekly:
                                if key in ind_tag.values_cumulative_weekly['sections_partners']:
                                    par_sec_cum_value += ind_tag.values_cumulative_weekly['sections_partners'][key]
                                    cum_partner_section['{}--{}--{}'.format(sec, par, tag.name)] = par_sec_cum_value
                indicator.values_tags_weekly['cum_section_partner_' + tag.name] = cum_partner_section

                # ------------ tags cumulative calculations per section per partner   -----------------

                cum_gov_section = {}

                for sec in sections:
                    sec = sec['reporting_section']
                    for gv in governorates:
                        gv = gv['location_adminlevel_governorate_code']
                        gov_sec_cum_value = 0
                        for ind_tag in tag_sub_indicators:
                            key = '{}-{}'.format(sec, gv)
                            if 'sections_govs' in ind_tag.values_cumulative_weekly:
                                if key in ind_tag.values_cumulative_weekly['sections_govs']:
                                    gov_sec_cum_value += ind_tag.values_cumulative_weekly['sections_govs'][key]
                                    cum_partner_gov['{}--{}--{}'.format(sec, gv, tag.name)] = gov_sec_cum_value
                indicator.values_tags_weekly['cum_sec_gov_' + tag.name] = cum_gov_section

                # -------------- tags cumulative calculations per section per partner  per gov ----------
                cum_partner_gov_section = {}
                for sec in sections:
                    sec = sec['reporting_section']
                    for par in partners:
                        par = par['partner_id']
                        for gv in governorates:
                            gv = gv['location_adminlevel_governorate_code']

                            par_gov_sec_cum_value = 0
                            for ind_tag in tag_sub_indicators:
                                key = '{}-{}-{}'.format(sec, par, gv)
                                if 'sections_partners_govs' in ind_tag.values_cumulative_weekly:
                                    if key in ind_tag.values_cumulative_weekly['sections_partners_govs']:
                                        par_gov_sec_cum_value += ind_tag.values_cumulative_weekly['sections_partners_govs'][key]
                                        cum_partner_gov_section['{}--{}--{}--{}'.format(sec, par, gv, tag.name)] = par_gov_sec_cum_value
                indicator.values_tags_weekly['cum_section_par_gov_' + tag.name] = cum_partner_gov_section

                # -------------- tags cumulative calculations per section per partner  per gov ----------
                cum_partner_gov_section = {}
                for sec in sections:
                    sec = sec['reporting_section']
                    for par in partners:
                        par = par['partner_id']
                        for gv in governorates:
                            gv = gv['location_adminlevel_governorate_code']

                            par_gov_sec_cum_value = 0
                            for ind_tag in tag_sub_indicators:
                                key = '{}-{}-{}'.format(sec, par, gv)
                                if 'sections_partners_govs' in ind_tag.values_cumulative_weekly:
                                    if key in ind_tag.values_cumulative_weekly['sections_partners_govs']:
                                        par_gov_sec_cum_value += ind_tag.values_cumulative_weekly['sections_partners_govs'][
                                            key]
                                        cum_partner_gov_section[
                                            '{}--{}--{}--{}'.format(sec, par, gv, tag.name)] = par_gov_sec_cum_value
                indicator.values_tags_weekly['cum_section_par_gov_' + tag.name] = cum_partner_gov_section

                # -------------- tags cumulative calculations per partner ----------
                cum_partner= {}
                for par in partners:
                    par = par['partner_id']
                    par_cum_value = 0
                    for ind_tag in tag_sub_indicators:
                        key = '{}'.format(par)
                        if 'partners' in ind_tag.values_cumulative_weekly:
                            if key in ind_tag.values_cumulative_weekly['partners']:
                                par_cum_value += ind_tag.values_cumulative_weekly['partners'][key]
                                cum_partner['{}--{}'.format(par, tag.name)] = par_cum_value
                indicator.values_tags_weekly['cum_partners_' + tag.name] = cum_partner

                # -------------- tags cumulative calculations per gov ----------
                cum_gov= {}
                for gv in governorates:
                    gv = gv['location_adminlevel_governorate_code']
                    gov_cum_value = 0
                    for ind_tag in tag_sub_indicators:
                        key = '{}'.format(gv)
                        if 'govs' in ind_tag.values_cumulative_weekly:
                            if key in ind_tag.values_cumulative_weekly['govs']:
                                gov_cum_value += ind_tag.values_cumulative_weekly['govs'][key]
                                cum_gov['{}--{}'.format(gv, tag.name)] = gov_cum_value
                indicator.values_tags_weekly['cum_govs_' + tag.name] = cum_gov


                # -------------- tags cumulative calculations per gov ----------
                cum_sec= {}
                for sec in sections:
                    sec = sec['reporting_section']
                    sec_cum_value = 0
                    for ind_tag in tag_sub_indicators:
                        key = '{}'.format(sec)
                        if 'sections' in ind_tag.values_cumulative_weekly:
                            if key in ind_tag.values_cumulative_weekly['sections']:
                                sec_cum_value += ind_tag.values_cumulative_weekly['sections'][key]
                                cum_sec['{}--{}'.format(sec, tag.name)] = sec_cum_value
                indicator.values_tags_weekly['cum_sections_' + tag.name] = cum_sec

                indicator.save()

                # -----------------  tags calculations General value and percentage  -----------------------
                value = 0
                for ind_tag in tag_sub_indicators:
                    c_value = 0
                    if 'months' in ind_tag.values_cumulative_weekly:
                        c_value = ind_tag.values_cumulative_weekly['months']

                    if isinstance(c_value, dict):
                        c_value = 0

                    value += float(c_value)

                try:
                    m_value = indicator.cumulative_values['months']

                except Exception:
                    continue

                tag_name_per = '{}_per'.format(tag.name)
                try:
                    indicator.values_tags_weekly[tag_name_per] = float(value) * 100 / float(m_value)
                    indicator.values_tags_weekly[tag.name] = value
                except Exception as ex:
                    # print(ex.message)
                    indicator.values_tags_weekly[tag_name_per] = 0
                    indicator.values_tags_weekly[tag.name] = 0

        # ----------------------------- Age groups tags --------------------------------
        for tag in tags_age.iterator():
            tag_sub_indicators = sub_indicators.filter(tag_age_id=tag.id)
            if tag_sub_indicators:

                partners_list = {}
                for mon in range(1, 13):
                    for par in partners:
                        par = par['partner_id']
                        par_value = 0
                        for ind_tag in tag_sub_indicators:
                            key = '{}-{}'.format(mon, par)
                            if key in ind_tag.values_partners_weekly:
                                par_value += ind_tag.values_partners_weekly[key]
                                partners_list['{}--{}--{}'.format(mon, par, tag.name)] = par_value

                indicator.values_tags_weekly['partners_' + tag.name] = partners_list

                govs_list = {}
                for mon in range(1, 13):
                    for gov in governorates:
                        gov = gov['location_adminlevel_governorate_code']
                        gov_value = 0
                        for ind_tag in tag_sub_indicators:
                            key = '{}-{}'.format(mon, gov)
                            if key in ind_tag.values_gov_weekly:
                                gov_value += ind_tag.values_gov_weekly[key]
                                govs_list['{}--{}--{}'.format(mon, gov, tag.name)] = gov_value

                indicator.values_tags_weekly['govs_' + tag.name] = govs_list

                sections_list = {}
                for mon in range(1, 13):
                    for sec in sections:
                        sec = sec['reporting_section']
                        sec_value = 0
                        for ind_tag in tag_sub_indicators:
                            key = '{}-{}'.format(mon, sec)
                            if ind_tag.values_sections:
                                if key in ind_tag.values_sections:
                                    sec_value += ind_tag.values_sections[key]
                                    sections_list['{}--{}--{}'.format(mon, sec, tag.name)] = sec_value

                indicator.values_tags_weekly['sections_' + tag.name] = sections_list

                partner_gov_list = {}
                for mon in range(1, 13):
                    for par in partners:
                        for gv in governorates:
                            par_gv_value = 0
                            for ind_tag in tag_sub_indicators:
                                key = '{}-{}-{}'.format(mon, gv, par)
                                if key in ind_tag.values_partners_gov_weekly:
                                    par_gv_value += ind_tag.values_partners_gov_weekly[key]
                                    partner_gov_list['{}--{}--{}--{}'.format(mon, par, gv, tag.name)] = par_gv_value

                indicator.values_tags_weekly['partners_govs_' + tag.name] = partner_gov_list

                partner_sec_list = {}
                for mon in range(1, 13):
                    for par in partners:
                        par = par['partner_id']
                        for sec in sections:
                            sec = sec['reporting_section']
                            par_sec_value = 0
                            for ind_tag in tag_sub_indicators:
                                key = '{}-{}-{}'.format(mon, sec, par)
                                if ind_tag.values_sections_partners:
                                    if key in ind_tag.values_sections_partners:
                                        par_sec_value += ind_tag.values_sections_partners[key]
                                        partner_sec_list['{}--{}--{}--{}'.format(mon, par, sec, tag.name)] = par_sec_value
                indicator.values_tags_weekly['partners_sections_' + tag.name] = partner_sec_list

                gov_sec_list = {}
                for mon in range(1, 13):
                    for gov in governorates:
                        gov = gov['location_adminlevel_governorate_code']
                        for sec in sections:
                            sec = sec['reporting_section']
                            gov_sec_value = 0
                            for ind_tag in tag_sub_indicators:
                                key = '{}-{}-{}'.format(mon, sec, gov)
                                if ind_tag.values_sections_gov:
                                    if key in ind_tag.values_sections_gov:
                                        gov_sec_value += ind_tag.values_sections_gov[key]
                                        gov_sec_list['{}--{}--{}--{}'.format(mon, gov, sec, tag.name)] = gov_sec_value
                indicator.values_tags_weekly['govs_sections_' + tag.name] = gov_sec_list

                # -----------------------------  tags calculations per gov per section per partner -----------------------

                partner_gov_sec_list = {}
                for mon in range(1, 13):
                    for sec in sections:
                        sec = sec['reporting_section']
                        for par in partners:
                            par = par['partner_id']
                            for gov in governorates:
                                gov = gov['location_adminlevel_governorate_code']
                                partner_gov_sec_value = 0
                                for ind_tag in tag_sub_indicators:
                                    key = '{}-{}-{}-{}'.format(mon, sec, par, gov)
                                    if ind_tag.values_sections_partners_gov:
                                        if key in ind_tag.values_sections_partners_gov:
                                            partner_gov_sec_value += ind_tag.values_sections_partners_gov[key]
                                            partner_gov_sec_list['{}--{}--{}--{}--{}'.format(mon, par, gov, sec,
                                                                                             tag.name)] = partner_gov_sec_value
                indicator.values_tags_weekly['partners_govs_sections_' + tag.name] = partner_gov_sec_list

                months_list = {}
                for mon in range(1, 13):
                    mon_value = 0
                    for ind_tag in tag_sub_indicators:
                        if str(mon) in ind_tag.values_weekly:
                            mon_value += ind_tag.values_weekly[str(mon)]
                    months_list['{}-{}'.format(mon, tag.name)] = mon_value

                indicator.values_tags_weekly['months_' + tag.name] = months_list

                cum_partner_gov = {}

                for gov in governorates:
                    gov = gov['location_adminlevel_governorate_code']
                    for par in partners:
                        par = par['partner_id']
                        par_gv_cum_value = 0
                        for ind_tag in tag_sub_indicators:
                            key = '{}-{}'.format(gov, par)
                            if 'partners_govs' in ind_tag.values_cumulative_weekly:
                                if key in ind_tag.values_cumulative_weekly['partners_govs']:
                                    par_gv_cum_value += ind_tag.values_cumulative_weekly['partners_govs'][key]
                                    cum_partner_gov['{}--{}--{}'.format(par, gov, tag.name)] = par_gv_cum_value
                indicator.values_tags_weekly['cum_partner_gov_' + tag.name] = cum_partner_gov

                cum_partner_section = {}

                for sec in sections:
                    sec = sec['reporting_section']
                    for par in partners:
                        par = par['partner_id']
                        par_sec_cum_value = 0
                        for ind_tag in tag_sub_indicators:
                            key = '{}-{}'.format(sec, par)
                            if 'sections_partners' in ind_tag.values_cumulative_weekly:
                                if key in ind_tag.values_cumulative_weekly['sections_partners']:
                                    par_sec_cum_value += ind_tag.values_cumulative_weekly['sections_partners'][key]
                                    cum_partner_gov['{}--{}--{}'.format(sec, par, tag.name)] = par_sec_cum_value
                indicator.values_tags_weekly['cum_section_partner_' + tag.name] = cum_partner_section

                cum_gov_section = {}

                for sec in sections:
                    sec = sec['reporting_section']
                    for gv in governorates:
                        gv = gv['location_adminlevel_governorate_code']
                        gov_sec_cum_value = 0
                        for ind_tag in tag_sub_indicators:
                            key = '{}-{}'.format(sec, gv)
                            if 'sections_govs' in ind_tag.values_cumulative_weekly:
                                if key in ind_tag.values_cumulative_weekly['sections_govs']:
                                    gov_sec_cum_value += ind_tag.values_cumulative_weekly['sections_govs'][key]
                                    cum_partner_gov['{}--{}--{}'.format(sec, gv, tag.name)] = gov_sec_cum_value
                indicator.values_tags_weekly['cum_section_gov_' + tag.name] = cum_gov_section

                cum_partner_gov_section = {}
                for sec in sections:
                    sec = sec['reporting_section']
                    for par in partners:
                        par = par['partner_id']
                        for gv in governorates:
                            gv = gv['location_adminlevel_governorate_code']

                            par_gov_sec_cum_value = 0
                            for ind_tag in tag_sub_indicators:
                                key = '{}-{}-{}'.format(sec, par, gv)
                                if 'sections_partners_govs' in ind_tag.values_cumulative_weekly:
                                    if key in ind_tag.values_cumulative_weekly['sections_partners_govs']:
                                        par_gov_sec_cum_value += ind_tag.values_cumulative_weekly['sections_partners_govs'][
                                            key]
                                        cum_partner_gov_section[
                                            '{}--{}--{}--{}'.format(sec, par, gv, tag.name)] = par_gov_sec_cum_value
                indicator.values_tags_weekly['cum_sec_par_gov_' + tag.name] = cum_partner_gov_section

                # -------------- tags cumulative calculations per partner ----------
                cum_partner = {}
                for par in partners:
                    par = par['partner_id']
                    par_cum_value = 0
                    for ind_tag in tag_sub_indicators:
                        key = '{}'.format(par)
                        if 'partners' in ind_tag.values_cumulative_weekly:
                            if key in ind_tag.values_cumulative_weekly['partners']:
                                par_cum_value += ind_tag.values_cumulative_weekly['partners'][key]
                                cum_partner['{}--{}'.format(par, tag.name)] = par_cum_value
                indicator.values_tags_weekly['cum_partners_' + tag.name] = cum_partner

                # -------------- tags cumulative calculations per gov ----------
                cum_gov = {}
                for gv in governorates:
                    gv = gv['location_adminlevel_governorate_code']
                    gov_cum_value = 0
                    for ind_tag in tag_sub_indicators:
                        key = '{}'.format(gv)
                        if 'govs' in ind_tag.values_cumulative_weekly:
                            if key in ind_tag.values_cumulative_weekly['govs']:
                                gov_cum_value += ind_tag.values_cumulative_weekly['govs'][key]
                                cum_gov['{}--{}'.format(gv, tag.name)] = gov_cum_value
                indicator.values_tags_weekly['cum_govs_' + tag.name] = cum_gov

                # -------------- tags cumulative calculations per gov ----------
                cum_sec = {}
                for sec in sections:
                    sec = sec['reporting_section']
                    sec_cum_value = 0
                    for ind_tag in tag_sub_indicators:
                        key = '{}'.format(sec)
                        if 'sections' in ind_tag.values_cumulative_weekly:
                            if key in ind_tag.values_cumulative_weekly['sections']:
                                sec_cum_value += ind_tag.values_cumulative_weekly['sections'][key]
                                cum_sec['{}--{}'.format(sec, tag.name)] = sec_cum_value
                indicator.values_tags_weekly['cum_sections_' + tag.name] = cum_sec

                indicator.save()

                value = 0
                for ind_tag in tag_sub_indicators:
                    c_value = 0
                    if 'months' in ind_tag.values_cumulative_weekly:
                        c_value = ind_tag.values_cumulative_weekly['months']

                    if isinstance(c_value, dict):
                        c_value = 0

                    value += float(c_value)

                tag_name_per = '{}_per'.format(tag.name)
                try:
                    indicator.values_tags_weekly[tag_name_per] = float(value) * 100 / float(m_value)
                    indicator.values_tags_weekly[tag.name] = value
                except Exception as ex:
                    # print(ex.message)
                    indicator.values_tags_weekly[tag_name_per] = 0
                    indicator.values_tags_weekly[tag.name] = 0

        # ----------------------------- Nationality tags --------------------------------
        for tag in tags_nationality.iterator():
            tag_sub_indicators = sub_indicators.filter(tag_nationality_id=tag.id)
            if tag_sub_indicators:

                partners_list = {}
                for mon in range(1, 13):
                    for par in partners:
                        par = par['partner_id']
                        par_value = 0
                        for ind_tag in tag_sub_indicators:
                            key = '{}-{}'.format(mon, par)
                            if key in ind_tag.values_partners_weekly:
                                par_value += ind_tag.values_partners_weekly[key]
                                partners_list['{}--{}--{}'.format(mon, par, tag.name)] = par_value

                indicator.values_tags_weekly['partners_' + tag.name] = partners_list

                govs_list = {}
                for mon in range(1, 13):
                    for gov in governorates:
                        gov = gov['location_adminlevel_governorate_code']
                        gov_value = 0
                        for ind_tag in tag_sub_indicators:
                            key = '{}-{}'.format(mon, gov)
                            if key in ind_tag.values_gov_weekly:
                                gov_value += ind_tag.values_gov_weekly[key]
                                govs_list['{}--{}--{}'.format(mon, gov, tag.name)] = gov_value

                indicator.values_tags_weekly['govs_' + tag.name] = govs_list

                sections_list = {}
                for mon in range(1, 13):
                    for sec in sections:
                        sec = sec['reporting_section']
                        sec_value = 0
                        for ind_tag in tag_sub_indicators:
                            key = '{}-{}'.format(mon, sec)
                            if ind_tag.values_sections:
                                if key in ind_tag.values_sections:
                                    sec_value += ind_tag.values_sections[key]
                                    sections_list['{}--{}--{}'.format(mon, sec, tag.name)] = sec_value

                indicator.values_tags_weekly['sections_' + tag.name] = sections_list

                partner_gov_list = {}
                for mon in range(1, 13):
                    for par in partners:
                        for gv in governorates:
                            par_gv_value = 0
                            for ind_tag in tag_sub_indicators:
                                key = '{}-{}-{}'.format(mon, gv, par)
                                if key in ind_tag.values_partners_gov_weekly:
                                    par_gv_value += ind_tag.values_partners_gov_weekly[key]
                                    partner_gov_list['{}--{}--{}--{}'.format(mon, par, gv, tag.name)] = par_gv_value

                indicator.values_tags_weekly['partners_govs_' + tag.name] = partner_gov_list

                partner_sec_list = {}
                for mon in range(1, 13):
                    for par in partners:
                        par = par['partner_id']
                        for sec in sections:
                            sec = sec['reporting_section']
                            par_sec_value = 0
                            for ind_tag in tag_sub_indicators:
                                key = '{}-{}-{}'.format(mon, sec, par)
                                if ind_tag.values_sections_partners:
                                    if key in ind_tag.values_sections_partners:
                                        par_sec_value += ind_tag.values_sections_partners[key]
                                        partner_sec_list['{}--{}--{}--{}'.format(mon, par, sec, tag.name)] = par_sec_value
                indicator.values_tags_weekly['partners_sections_' + tag.name] = partner_sec_list

                gov_sec_list = {}
                for mon in range(1, 13):
                    for gov in governorates:
                        gov = gov['location_adminlevel_governorate_code']
                        for sec in sections:
                            sec = sec['reporting_section']
                            gov_sec_value = 0
                            for ind_tag in tag_sub_indicators:
                                key = '{}-{}-{}'.format(mon, sec, gov)
                                if ind_tag.values_sections_gov:
                                    if key in ind_tag.values_sections_gov:
                                        gov_sec_value += ind_tag.values_sections_gov[key]
                                        gov_sec_list['{}--{}--{}--{}'.format(mon, gov, sec, tag.name)] = gov_sec_value
                indicator.values_tags_weekly['govs_sections_' + tag.name] = gov_sec_list

                # -----------------------------  tags calculations per gov per section per partner -----------------------

                partner_gov_sec_list = {}
                for mon in range(1, 13):
                    for sec in sections:
                        sec = sec['reporting_section']
                        for par in partners:
                            par = par['partner_id']
                            for gov in governorates:
                                gov = gov['location_adminlevel_governorate_code']
                                partner_gov_sec_value = 0
                                for ind_tag in tag_sub_indicators:
                                    key = '{}-{}-{}-{}'.format(mon, sec, par, gov)
                                    if ind_tag.values_sections_partners_gov:
                                        if key in ind_tag.values_sections_partners_gov:
                                            partner_gov_sec_value += ind_tag.values_sections_partners_gov[key]
                                            partner_gov_sec_list['{}--{}--{}--{}--{}'.format(mon, par, gov, sec,
                                                                                             tag.name)] = partner_gov_sec_value
                indicator.values_tags_weekly['partners_govs_sections_' + tag.name] = partner_gov_sec_list

                months_list = {}
                for mon in range(1, 13):
                    mon_value = 0
                    for ind_tag in tag_sub_indicators:
                        if str(mon) in ind_tag.values_weekly:
                            mon_value += ind_tag.values_weekly[str(mon)]
                    months_list['{}-{}'.format(mon, tag.name)] = mon_value

                indicator.values_tags_weekly['months_' + tag.name] = months_list

                cum_partner_gov = {}

                for gov in governorates:
                    gov = gov['location_adminlevel_governorate_code']
                    for par in partners:
                        par = par['partner_id']
                        par_gv_cum_value = 0
                        for ind_tag in tag_sub_indicators:
                            key = '{}-{}'.format(gov, par)
                            if 'partners_govs' in ind_tag.values_cumulative_weekly:
                                if key in ind_tag.values_cumulative_weekly['partners_govs']:
                                    par_gv_cum_value += ind_tag.values_cumulative_weekly['partners_govs'][key]
                                    cum_partner_gov['{}--{}--{}'.format(par, gov, tag.name)] = par_gv_cum_value
                indicator.values_tags_weekly['cum_partner_gov_' + tag.name] = cum_partner_gov

                cum_partner_section = {}
                for sec in sections:
                    sec = sec['reporting_section']
                    for par in partners:
                        par = par['partner_id']
                        par_sec_cum_value = 0
                        for ind_tag in tag_sub_indicators:
                            key = '{}-{}'.format(sec, par)
                            if 'sections_partners' in ind_tag.values_cumulative_weekly:
                                if key in ind_tag.values_cumulative_weekly['sections_partners']:
                                    par_sec_cum_value += ind_tag.values_cumulative_weekly['sections_partners'][key]
                                    cum_partner_gov['{}--{}--{}'.format(sec, par, tag.name)] = par_sec_cum_value
                indicator.values_tags_weekly['cum_section_partner_' + tag.name] = cum_partner_section

                cum_gov_section = {}
                for sec in sections:
                    sec = sec['reporting_section']
                    for gv in governorates:
                        gv = gv['location_adminlevel_governorate_code']
                        gov_sec_cum_value = 0
                        for ind_tag in tag_sub_indicators:
                            key = '{}-{}'.format(sec, gv)
                            if 'sections_govs' in ind_tag.values_cumulative_weekly:
                                if key in ind_tag.values_cumulative_weekly['sections_govs']:
                                    gov_sec_cum_value += ind_tag.values_cumulative_weekly['sections_govs'][key]
                                    cum_partner_gov['{}--{}--{}'.format(sec, gv, tag.name)] = gov_sec_cum_value
                indicator.values_tags_weekly['cum_section_gov_' + tag.name] = cum_gov_section

                cum_partner_gov_section = {}
                for sec in sections:
                    sec = sec['reporting_section']
                    for par in partners:
                        par = par['partner_id']
                        for gv in governorates:
                            gv = gv['location_adminlevel_governorate_code']

                            par_gov_sec_cum_value = 0
                            for ind_tag in tag_sub_indicators:
                                key = '{}-{}-{}'.format(sec, par, gv)
                                if 'sections_partners_govs' in ind_tag.values_cumulative_weekly:
                                    if key in ind_tag.values_cumulative_weekly['sections_partners_govs']:
                                        par_gov_sec_cum_value += ind_tag.values_cumulative_weekly['sections_partners_govs'][
                                            key]
                                        cum_partner_gov_section[
                                            '{}--{}--{}--{}'.format(sec, par, gv, tag.name)] = par_gov_sec_cum_value
                indicator.values_tags_weekly['cum_sec_par_gov_' + tag.name] = cum_partner_gov_section

                # -------------- tags cumulative calculations per partner ----------
                cum_partner = {}
                for par in partners:
                    par = par['partner_id']
                    par_cum_value = 0
                    for ind_tag in tag_sub_indicators:
                        key = '{}'.format(par)
                        if 'partners' in ind_tag.values_cumulative_weekly:
                            if key in ind_tag.values_cumulative_weekly['partners']:
                                par_cum_value += ind_tag.values_cumulative_weekly['partners'][key]
                                cum_partner['{}--{}'.format(par, tag.name)] = par_cum_value
                indicator.values_tags_weekly['cum_partners_' + tag.name] = cum_partner

                # -------------- tags cumulative calculations per gov ----------
                cum_gov = {}
                for gv in governorates:
                    gv = gv['location_adminlevel_governorate_code']
                    gov_cum_value = 0
                    for ind_tag in tag_sub_indicators:
                        key = '{}'.format(gv)
                        if 'govs' in ind_tag.values_cumulative_weekly:
                            if key in ind_tag.values_cumulative_weekly['govs']:
                                gov_cum_value += ind_tag.values_cumulative_weekly['govs'][key]
                                cum_gov['{}--{}'.format(gv, tag.name)] = gov_cum_value
                indicator.values_tags_weekly['cum_govs_' + tag.name] = cum_gov

                # -------------- tags cumulative calculations per gov ----------
                cum_sec = {}
                for sec in sections:
                    sec = sec['reporting_section']
                    sec_cum_value = 0
                    for ind_tag in tag_sub_indicators:
                        key = '{}'.format(sec)
                        if 'sections' in ind_tag.values_cumulative_weekly:
                            if key in ind_tag.values_cumulative_weekly['sections']:
                                sec_cum_value += ind_tag.values_cumulative_weekly['sections'][key]
                                cum_sec['{}--{}'.format(sec, tag.name)] = sec_cum_value
                indicator.values_tags_weekly['cum_sections_' + tag.name] = cum_sec

                indicator.save()

                value = 0
                for ind_tag in tag_sub_indicators:
                    c_value = 0
                    if 'months' in ind_tag.values_cumulative_weekly:
                        c_value = ind_tag.values_cumulative_weekly['months']

                    if isinstance(c_value, dict):
                        c_value = 0

                    value += float(c_value)

                tag_name_per = '{}_per'.format(tag.name)
                try:
                    indicator.values_tags_weekly[tag_name_per] = float(value) * 100 / float(m_value)
                    indicator.values_tags_weekly[tag.name] = value
                except Exception as ex:
                    # print(ex.message)
                    indicator.values_tags_weekly[tag_name_per] = 0
                    indicator.values_tags_weekly[tag.name] = 0

        # ----------------------------- Programme tags --------------------------------
        for tag in tags_programme.iterator():
            tag_sub_indicators = sub_indicators.filter(tag_programme_id=tag.id)
            if tag_sub_indicators:

                partners_list = {}
                for mon in range(1, 13):
                    for par in partners:
                        par = par['partner_id']
                        par_value = 0
                        for ind_tag in tag_sub_indicators:
                            key = '{}-{}'.format(mon, par)
                            if key in ind_tag.values_partners_weekly:
                                par_value += ind_tag.values_partners_weekly[key]
                                partners_list['{}--{}--{}'.format(mon, par, tag.name)] = par_value

                indicator.values_tags_weekly['partners_' + tag.name] = partners_list

                govs_list = {}
                for mon in range(1, 13):
                    for gov in governorates:
                        gov = gov['location_adminlevel_governorate_code']
                        gov_value = 0
                        for ind_tag in tag_sub_indicators:
                            key = '{}-{}'.format(mon, gov)
                            if key in ind_tag.values_gov_weekly:
                                gov_value += ind_tag.values_gov_weekly[key]
                                govs_list['{}--{}--{}'.format(mon, gov, tag.name)] = gov_value
                indicator.values_tags_weekly['govs_' + tag.name] = govs_list

                sections_list = {}
                for mon in range(1, 13):
                    for sec in sections:
                        sec = sec['reporting_section']
                        sec_value = 0
                        for ind_tag in tag_sub_indicators:
                            key = '{}-{}'.format(mon, sec)
                            if ind_tag.values_sections:
                                if key in ind_tag.values_sections:
                                    sec_value += ind_tag.values_sections[key]
                                    sections_list['{}--{}--{}'.format(mon, sec, tag.name)] = sec_value
                indicator.values_tags_weekly['sections_' + tag.name] = sections_list

                partner_gov_list = {}
                for mon in range(1, 13):
                    for par in partners:
                        for gv in governorates:
                            par_gv_value = 0
                            for ind_tag in tag_sub_indicators:
                                key = '{}-{}-{}'.format(mon, gv, par)
                                if key in ind_tag.values_partners_gov_weekly:
                                    par_gv_value += ind_tag.values_partners_gov_weekly[key]
                                    partner_gov_list['{}--{}--{}--{}'.format(mon, par, gv, tag.name)] = par_gv_value

                indicator.values_tags_weekly['partners_govs_' + tag.name] = partner_gov_list

                partner_sec_list = {}
                for mon in range(1, 13):
                    for par in partners:
                        par = par['partner_id']
                        for sec in sections:
                            sec = sec['reporting_section']
                            par_sec_value = 0
                            for ind_tag in tag_sub_indicators:
                                key = '{}-{}-{}'.format(mon, sec, par)
                                if ind_tag.values_sections_partners:
                                    if key in ind_tag.values_sections_partners:
                                        par_sec_value += ind_tag.values_sections_partners[key]
                                        partner_sec_list['{}--{}--{}--{}'.format(mon, par, sec, tag.name)] = par_sec_value
                indicator.values_tags_weekly['partners_sections_' + tag.name] = partner_sec_list

                gov_sec_list = {}
                for mon in range(1, 13):
                    for gov in governorates:
                        gov = gov['location_adminlevel_governorate_code']
                        for sec in sections:
                            sec = sec['reporting_section']
                            gov_sec_value = 0
                            for ind_tag in tag_sub_indicators:
                                key = '{}-{}-{}'.format(mon, sec, gov)
                                if ind_tag.values_sections_gov:
                                    if key in ind_tag.values_sections_gov:
                                        gov_sec_value += ind_tag.values_sections_gov[key]
                                        gov_sec_list['{}--{}--{}--{}'.format(mon, gov, sec, tag.name)] = gov_sec_value
                indicator.values_tags_weekly['govs_sections_' + tag.name] = gov_sec_list

                # -----------------------------  tags calculations per gov per section per partner -----------------------

                partner_gov_sec_list = {}
                for mon in range(1, 13):
                    for sec in sections:
                        sec = sec['reporting_section']
                        for par in partners:
                            par = par['partner_id']
                            for gov in governorates:
                                gov = gov['location_adminlevel_governorate_code']
                                partner_gov_sec_value = 0
                                for ind_tag in tag_sub_indicators:
                                    key = '{}-{}-{}-{}'.format(mon, sec, par, gov)
                                    if key in ind_tag.values_sections_partners_gov:
                                        partner_gov_sec_value += ind_tag.values_sections_partners_gov[key]
                                        partner_gov_sec_list['{}--{}--{}--{}--{}'.format(mon, par, gov, sec,
                                                                                         tag.name)] = partner_gov_sec_value
                indicator.values_tags_weekly['partners_govs_sections_' + tag.name] = partner_gov_sec_list

                months_list = {}
                for mon in range(1, 13):
                    mon_value = 0
                    for ind_tag in tag_sub_indicators:
                        if str(mon) in ind_tag.values_weekly:
                            mon_value += ind_tag.values_weekly[str(mon)]
                    months_list['{}-{}'.format(mon, tag.name)] = mon_value
                indicator.values_tags_weekly['months_' + tag.name] = months_list

                cum_partner_gov = {}

                for gov in governorates:
                    gov = gov['location_adminlevel_governorate_code']
                    for par in partners:
                        par = par['partner_id']
                        par_gv_cum_value = 0
                        for ind_tag in tag_sub_indicators:
                            key = '{}-{}'.format(gov, par)
                            if 'partners_govs' in ind_tag.values_cumulative_weekly:
                                if key in ind_tag.values_cumulative_weekly['partners_govs']:
                                    par_gv_cum_value += ind_tag.values_cumulative_weekly['partners_govs'][key]
                                    cum_partner_gov['{}--{}--{}'.format(par, gov, tag.name)] = par_gv_cum_value
                indicator.values_tags_weekly['cum_partner_gov_' + tag.name] = cum_partner_gov

                cum_partner_section = {}
                for sec in sections:
                    sec = sec['reporting_section']
                    for par in partners:
                        par = par['partner_id']
                        par_sec_cum_value = 0
                        for ind_tag in tag_sub_indicators:
                            key = '{}-{}'.format(sec, par)
                            if 'sections_partners' in ind_tag.values_cumulative_weekly:
                                if key in ind_tag.values_cumulative_weekly['sections_partners']:
                                    par_sec_cum_value += ind_tag.values_cumulative_weekly['sections_partners'][key]
                                    cum_partner_gov['{}--{}--{}'.format(sec, par, tag.name)] = par_sec_cum_value
                indicator.values_tags_weekly['cum_section_partner_' + tag.name] = cum_partner_section

                cum_gov_section = {}

                for sec in sections:
                    sec = sec['reporting_section']
                    for gv in governorates:
                        gv = gv['location_adminlevel_governorate_code']
                        gov_sec_cum_value = 0
                        for ind_tag in tag_sub_indicators:
                            key = '{}-{}'.format(sec, gv)
                            if 'sections_govs' in ind_tag.values_cumulative_weekly:
                                if key in ind_tag.values_cumulative_weekly['sections_govs']:
                                    gov_sec_cum_value += ind_tag.values_cumulative_weekly['sections_govs'][key]
                                    cum_partner_gov['{}--{}--{}'.format(sec, gv, tag.name)] = gov_sec_cum_value
                indicator.values_tags_weekly['cum_section_gov_' + tag.name] = cum_gov_section

                cum_partner_gov_section = {}
                for sec in sections:
                    sec = sec['reporting_section']
                    for par in partners:
                        par = par['partner_id']
                        for gv in governorates:
                            gv = gv['location_adminlevel_governorate_code']

                            par_gov_sec_cum_value = 0
                            for ind_tag in tag_sub_indicators:
                                key = '{}-{}-{}'.format(sec, par, gv)
                                if 'sections_partners_govs' in ind_tag.values_cumulative_weekly:
                                    if key in ind_tag.values_cumulative_weekly['sections_partners_govs']:
                                        par_gov_sec_cum_value += ind_tag.values_cumulative_weekly['sections_partners_govs'][
                                            key]
                                        cum_partner_gov_section[
                                            '{}--{}--{}--{}'.format(sec, par, gv, tag.name)] = par_gov_sec_cum_value
                indicator.values_tags_weekly['cum_sec_par_gov_' + tag.name] = cum_partner_gov_section

                # -------------- tags cumulative calculations per partner ----------
                cum_partner = {}
                for par in partners:
                    par = par['partner_id']
                    par_cum_value = 0
                    for ind_tag in tag_sub_indicators:
                        key = '{}'.format(par)
                        if 'partners' in ind_tag.values_cumulative_weekly:
                            if key in ind_tag.values_cumulative_weekly['partners']:
                                par_cum_value += ind_tag.values_cumulative_weekly['partners'][key]
                                cum_partner['{}--{}'.format(par, tag.name)] = par_cum_value
                indicator.values_tags_weekly['cum_partners_' + tag.name] = cum_partner

                # -------------- tags cumulative calculations per gov ----------
                cum_gov = {}
                for gv in governorates:
                    gv = gv['location_adminlevel_governorate_code']
                    gov_cum_value = 0
                    for ind_tag in tag_sub_indicators:
                        key = '{}'.format(gv)
                        if 'govs' in ind_tag.values_cumulative_weekly:
                            if key in ind_tag.values_cumulative_weekly['govs']:
                                gov_cum_value += ind_tag.values_cumulative_weekly['govs'][key]
                                cum_gov['{}--{}'.format(gv, tag.name)] = gov_cum_value
                indicator.values_tags_weekly['cum_govs_' + tag.name] = cum_gov

                # -------------- tags cumulative calculations per gov ----------
                cum_sec = {}
                for sec in sections:
                    sec = sec['reporting_section']
                    sec_cum_value = 0
                    for ind_tag in tag_sub_indicators:
                        key = '{}'.format(sec)
                        if 'sections' in ind_tag.values_cumulative_weekly:
                            if key in ind_tag.values_cumulative_weekly['sections']:
                                sec_cum_value += ind_tag.values_cumulative_weekly['sections'][key]
                                cum_sec['{}--{}'.format(sec, tag.name)] = sec_cum_value
                indicator.values_tags_weekly['cum_sections_' + tag.name] = cum_sec

                indicator.save()

                value = 0
                for ind_tag in tag_sub_indicators:
                    c_value = 0
                    if 'months' in ind_tag.values_cumulative_weekly:
                        c_value = ind_tag.values_cumulative_weekly['months']

                    if isinstance(c_value, dict):
                        c_value = 0

                    value += float(c_value)

                tag_name_per = '{}_per'.format(tag.name)
                try:
                    indicator.values_tags_weekly[tag_name_per] = float(value) * 100 / float(m_value)
                    indicator.values_tags_weekly[tag.name] = value
                except Exception as ex:
                    # print(ex.message)
                    indicator.values_tags_weekly[tag_name_per] = 0
                    indicator.values_tags_weekly[tag.name] = 0

        # ----------------------------- Disability tags --------------------------------

        for tag in tags_disability.iterator():
            tag_sub_indicators = sub_indicators.filter(tag_disability_id=tag.id)

            if tag_sub_indicators:

                partners_list = {}
                for mon in range(1, 13):
                    for par in partners:
                        par = par['partner_id']
                        par_value = 0
                        for ind_tag in tag_sub_indicators:
                            key = '{}-{}'.format(mon, par)
                            if key in ind_tag.values_partners_weekly:
                                par_value += ind_tag.values_partners_weekly[key]
                                partners_list['{}--{}--{}'.format(mon, par, tag.name)] = par_value
                indicator.values_tags_weekly['partners_' + tag.name] = partners_list

                govs_list = {}
                for mon in range(1, 13):
                    for gov in governorates:
                        gov = gov['location_adminlevel_governorate_code']
                        gov_value = 0
                        for ind_tag in tag_sub_indicators:
                            key = '{}-{}'.format(mon, gov)
                            if key in ind_tag.values_gov_weekly:
                                gov_value += ind_tag.values_gov_weekly[key]
                                govs_list['{}--{}--{}'.format(mon, gov, tag.name)] = gov_value
                indicator.values_tags_weekly['govs_' + tag.name] = govs_list

                sections_list = {}
                for mon in range(1, 13):
                    for sec in sections:
                        sec = sec['reporting_section']
                        sec_value = 0
                        for ind_tag in tag_sub_indicators:
                            key = '{}-{}'.format(mon, sec)
                            if ind_tag.values_sections:
                                if key in ind_tag.values_sections:
                                    sec_value += ind_tag.values_sections[key]
                                    sections_list['{}--{}--{}'.format(mon, sec, tag.name)] = sec_value

                indicator.values_tags_weekly['sections_' + tag.name] = sections_list

                partner_gov_list = {}
                for mon in range(1, 13):
                    for par in partners:
                        for gv in governorates:
                            par_gv_value = 0
                            for ind_tag in tag_sub_indicators:
                                key = '{}-{}-{}'.format(mon, gv, par)
                                if key in ind_tag.values_partners_gov:
                                    par_gv_value += ind_tag.values_partners_gov[key]
                                    partner_gov_list['{}--{}--{}--{}'.format(mon, par, gv, tag.name)] = par_gv_value

                indicator.values_tags_weekly['partners_govs_' + tag.name] = partner_gov_list

                partner_sec_list = {}
                for mon in range(1, 13):
                    for par in partners:
                        par = par['partner_id']
                        for sec in sections:
                            sec = sec['reporting_section']
                            par_sec_value = 0
                            for ind_tag in tag_sub_indicators:
                                key = '{}-{}-{}'.format(mon, sec, par)
                                if ind_tag.values_sections_partners:
                                    if key in ind_tag.values_sections_partners:
                                        par_sec_value += ind_tag.values_sections_partners[key]
                                        partner_sec_list['{}--{}--{}--{}'.format(mon, par, sec, tag.name)] = par_sec_value
                indicator.values_tags_weekly['partners_sections_' + tag.name] = partner_sec_list

                gov_sec_list = {}
                for mon in range(1, 13):
                    for gov in governorates:
                        gov = gov['location_adminlevel_governorate_code']
                        for sec in sections:
                            sec = sec['reporting_section']
                            gov_sec_value = 0
                            for ind_tag in tag_sub_indicators:
                                key = '{}-{}-{}'.format(mon, sec, gov)
                                if ind_tag.values_sections_gov:
                                    if key in ind_tag.values_sections_gov:
                                        gov_sec_value += ind_tag.values_sections_gov[key]
                                        gov_sec_list['{}--{}--{}--{}'.format(mon, gov, sec, tag.name)] = gov_sec_value
                indicator.values_tags_weekly['govs_sections_' + tag.name] = gov_sec_list

                # -----------------------------  tags calculations per gov per section per partner -----------------------

                partner_gov_sec_list = {}
                for mon in range(1, 13):
                    for sec in sections:
                        sec = sec['reporting_section']
                        for par in partners:
                            par = par['partner_id']
                            for gov in governorates:
                                gov = gov['location_adminlevel_governorate_code']
                                partner_gov_sec_value = 0
                                for ind_tag in tag_sub_indicators:
                                    key = '{}-{}-{}-{}'.format(mon, sec, par, gov)
                                    if ind_tag.values_sections_partners_gov:
                                        if key in ind_tag.values_sections_partners_gov:
                                            partner_gov_sec_value += ind_tag.values_sections_partners_gov[key]
                                            partner_gov_sec_list['{}--{}--{}--{}--{}'.format(mon, par, gov, sec,
                                                                                             tag.name)] = partner_gov_sec_value
                indicator.values_tags_weekly['partners_govs_sections_' + tag.name] = partner_gov_sec_list

                months_list = {}
                for mon in range(1, 13):
                    mon_value = 0
                    for ind_tag in tag_sub_indicators:
                        if str(mon) in ind_tag.values_weekly:
                            mon_value += ind_tag.values_weekly[str(mon)]
                    months_list['{}-{}'.format(mon, tag.name)] = mon_value

                indicator.values_tags_weekly['months_' + tag.name] = months_list

                cum_partner_gov = {}
                for gov in governorates:
                    gov = gov['location_adminlevel_governorate_code']
                    for par in partners:
                        par = par['partner_id']
                        par_gv_cum_value = 0
                        for ind_tag in tag_sub_indicators:
                            key = '{}-{}'.format(gov, par)
                            if 'partners_govs' in ind_tag.values_cumulative_weekly:
                                if key in ind_tag.values_cumulative_weekly['partners_govs']:
                                    par_gv_cum_value += ind_tag.values_cumulative_weekly['partners_govs'][key]
                                    cum_partner_gov['{}--{}--{}'.format(par, gov, tag.name)] = par_gv_cum_value
                indicator.values_tags_weekly['cum_partner_gov_' + tag.name] = cum_partner_gov

                cum_partner_section = {}
                for sec in sections:
                    sec = sec['reporting_section']
                    for par in partners:
                        par = par['partner_id']
                        par_sec_cum_value = 0
                        for ind_tag in tag_sub_indicators:
                            key = '{}-{}'.format(sec, par)
                            if 'sections_partners' in ind_tag.values_cumulative_weekly:
                                if key in ind_tag.values_cumulative_weekly['sections_partners']:
                                    par_sec_cum_value += ind_tag.values_cumulative_weekly['sections_partners'][key]
                                    cum_partner_gov['{}--{}--{}'.format(sec, par, tag.name)] = par_sec_cum_value
                indicator.values_tags_weekly['cum_section_partner_' + tag.name] = cum_partner_section

                cum_gov_section = {}

                for sec in sections:
                    sec = sec['reporting_section']
                    for gv in governorates:
                        gv = gv['location_adminlevel_governorate_code']
                        gov_sec_cum_value = 0
                        for ind_tag in tag_sub_indicators:
                            key = '{}-{}'.format(sec, gv)
                            if 'sections_govs' in ind_tag.values_cumulative_weekly:
                                if key in ind_tag.values_cumulative_weekly['sections_govs']:
                                    gov_sec_cum_value += ind_tag.cumulative_values['sections_govs'][key]
                                    cum_partner_gov['{}--{}--{}'.format(sec, gv, tag.name)] = gov_sec_cum_value
                indicator.values_tags_weekly['cum_sec_gov_' + tag.name] = cum_gov_section

                cum_partner_gov_section = {}
                for sec in sections:
                    sec = sec['reporting_section']
                    for par in partners:
                        par = par['partner_id']
                        for gv in governorates:
                            gv = gv['location_adminlevel_governorate_code']

                            par_gov_sec_cum_value = 0
                            for ind_tag in tag_sub_indicators:
                                key = '{}-{}-{}'.format(sec, par, gv)
                                if 'sections_partners_govs' in ind_tag.values_cumulative_weekly:
                                    if key in ind_tag.values_cumulative_weekly['sections_partners_govs']:
                                        par_gov_sec_cum_value += ind_tag.values_cumulative_weekly['sections_partners_govs'][
                                            key]
                                        cum_partner_gov_section[
                                            '{}--{}--{}--{}'.format(sec, par, gv, tag.name)] = par_gov_sec_cum_value
                indicator.values_tags_weekly['cum_sec_par_gov_' + tag.name] = cum_partner_gov_section

                # -------------- tags cumulative calculations per partner ----------
                cum_partner = {}
                for par in partners:
                    par = par['partner_id']
                    par_cum_value = 0
                    for ind_tag in tag_sub_indicators:
                        key = '{}'.format(par)
                        if 'partners' in ind_tag.values_cumulative_weekly:
                            if key in ind_tag.values_cumulative_weekly['partners']:
                                par_cum_value += ind_tag.values_cumulative_weekly['partners'][key]
                                cum_partner['{}--{}'.format(par, tag.name)] = par_cum_value
                indicator.values_tags_weekly['cum_partners_' + tag.name] = cum_partner

                # -------------- tags cumulative calculations per gov ----------
                cum_gov = {}
                for gv in governorates:
                    gv = gv['location_adminlevel_governorate_code']
                    gov_cum_value = 0
                    for ind_tag in tag_sub_indicators:
                        key = '{}'.format(gv)
                        if 'govs' in ind_tag.values_cumulative_weekly:
                            if key in ind_tag.values_cumulative_weekly['govs']:
                                gov_cum_value += ind_tag.values_cumulative_weekly['govs'][key]
                                cum_gov['{}--{}'.format(gv, tag.name)] = gov_cum_value
                indicator.values_tags_weekly['cum_govs_' + tag.name] = cum_gov

                # -------------- tags cumulative calculations per section ----------
                cum_sec = {}
                for sec in sections:
                    sec = sec['reporting_section']
                    sec_cum_value = 0
                    for ind_tag in tag_sub_indicators:
                        key = '{}'.format(sec)
                        if 'sections' in ind_tag.values_cumulative_weekly:
                            if key in ind_tag.values_cumulative_weekly['sections']:
                                sec_cum_value += ind_tag.values_cumulative_weekly['sections'][key]
                                cum_sec['{}--{}'.format(sec, tag.name)] = sec_cum_value
                indicator.values_tags_weekly['cum_sections_' + tag.name] = cum_sec

                indicator.save()

                value = 0
                for ind_tag in tag_sub_indicators:
                    c_value = 0
                    if 'months' in ind_tag.values_cumulative_weekly:
                        c_value = ind_tag.values_cumulative_weekly['months']

                    if isinstance(c_value, dict):
                        c_value = 0

                    value += float(c_value)

                tag_name_per = '{}_per'.format(tag.name)
                try:
                    indicator.values_tags_weekly[tag_name_per] = float(value) * 100 / float(m_value)
                    indicator.values_tags_weekly[tag.name] = value
                except Exception as ex:
                    # print(ex.message)
                    indicator.values_tags_weekly[tag_name_per] = 0
                    indicator.values_tags_weekly[tag.name] = 0

            indicator.save()

    return indicators.count()


def calculate_indicators_monthly_tags(ai_db):
    from internos.activityinfo.models import Indicator, IndicatorTag

    # indicators = Indicator.objects.filter(hpm_indicator=True)
    indicators = Indicator.objects.filter(Q(master_indicator=True) | Q(hpm_indicator=True))
    # indicators = Indicator.objects.filter(id=3985)
    tags_gender = IndicatorTag.objects.filter(type='gender').only('id', 'name')
    tags_age = IndicatorTag.objects.filter(type='age').only('id', 'name')
    tags_nationality = IndicatorTag.objects.filter(type='nationality').only('id', 'name')
    tags_disability = IndicatorTag.objects.filter(type='disability').only('id', 'name')
    tags_programme = IndicatorTag.objects.filter(type='programme').only('id', 'name')

    today = datetime.date.today()
    first = today.replace(day=1)
    last_month = first - datetime.timedelta(days=1)
    month = int(last_month.strftime("%m"))
    # month = int(last_month.strftime("%m")) - 1
    month_str = str(month)

    month = 12
    month_str = 'December'

    for indicator in indicators.iterator():
        sub_indicators = indicator.summation_sub_indicators.all().only(
            'cumulative_values_hpm',
            'values',
        )

        if not indicator.cumulative_values_hpm:
            indicator.cumulative_values_hpm = {}
        if 'tags' not in indicator.cumulative_values_hpm:
            indicator.cumulative_values_hpm['tags'] = {}

        for tag in tags_gender.iterator():
            tag_sub_indicators = sub_indicators.filter(tag_gender_id=tag.id)

            value = 0
            for ind_tag in tag_sub_indicators:
                c_value = 0
                if month_str in ind_tag.values:
                    c_value = ind_tag.values[month_str]

                value += float(c_value)

            key = '{}-{}'.format(month, tag.name)
            try:
                indicator.cumulative_values_hpm['tags'][key] = value
            except Exception as ex:
                # print(ex.message)
                indicator.cumulative_values_hpm['tags'][key] = 0

        for tag in tags_age.iterator():
            tag_sub_indicators = sub_indicators.filter(tag_age_id=tag.id)

            value = 0
            for ind_tag in tag_sub_indicators:
                c_value = 0
                if month_str in ind_tag.values:
                    c_value = ind_tag.values[month_str]

                value += float(c_value)

            key = '{}-{}'.format(month_str, tag.name)
            try:
                indicator.cumulative_values_hpm['tags'][key] = value
            except Exception as ex:
                # print(ex.message)
                indicator.cumulative_values_hpm['tags'][key] = 0

        for tag in tags_nationality.iterator():
            tag_sub_indicators = sub_indicators.filter(tag_nationality_id=tag.id)

            value = 0
            for ind_tag in tag_sub_indicators:
                c_value = 0
                if month_str in ind_tag.values:
                    c_value = ind_tag.values[month_str]

                value += float(c_value)

            key = '{}-{}'.format(month, tag.name)
            try:
                indicator.cumulative_values_hpm['tags'][key] = value
            except Exception as ex:
                # print(ex.message)
                indicator.cumulative_values_hpm['tags'][key] = 0

        for tag in tags_programme.iterator():
            tag_sub_indicators = sub_indicators.filter(tag_programme_id=tag.id)

            value = 0
            for ind_tag in tag_sub_indicators:
                c_value = 0
                if month_str in ind_tag.values:
                    c_value = ind_tag.values[month_str]

                value += float(c_value)

            key = '{}-{}'.format(month, tag.name)
            try:
                indicator.cumulative_values_hpm['tags'][key] = value
            except Exception as ex:
                # print(ex.message)
                indicator.cumulative_values_hpm['tags'][key] = 0

        for tag in tags_disability.iterator():
            tag_sub_indicators = sub_indicators.filter(tag_disability_id=tag.id)

            value = 0
            for ind_tag in tag_sub_indicators:
                c_value = 0
                if month_str in ind_tag.values:
                    c_value = ind_tag.values[month_str]

                value += float(c_value)

            key = '{}-{}'.format(month, tag.name)
            try:
                indicator.cumulative_values_hpm['tags'][key] = value
            except Exception as ex:
                # print(ex.message)
                indicator.cumulative_values_hpm['tags'][key] = 0

        indicator.save()

    return indicators.count()


def calculate_master_indicators_values_1(ai_db, report_type=None, sub_indicators=False):
    from django.db import connection
    from internos.activityinfo.models import Indicator

    if sub_indicators:
        indicators = Indicator.objects.filter(activity__database__ai_id=ai_db.ai_id,
                                              master_indicator_sub=True)
    else:
        indicators = Indicator.objects.filter(activity__database__ai_id=ai_db.ai_id,
                                              master_indicator=True)

    indicators = indicators.only(
            'id',
            'values_weekly',
            'values_gov_weekly',
            'values_partners_weekly',
            'values_partners_gov_weekly',
            'values_crisis_live',
            'values_crisis_gov_live',
            'values_crisis_partners_live',
            'values_crisis_partners_gov_live',
            'values_sections',
            'values_sections_partners',
            'values_sections_gov',
            'values_sections_partners_gov',
            'values_sections_live',
            'values_sections_partners_live',
            'values_sections_gov_live',
            'values_sections_partners_gov_live',

    )

    rows_data = {}
    cursor = connection.cursor()
    cursor.execute(
             "SELECT distinct a1.id, ai.id, ai.values_weekly ,ai.values_crisis_live  ,ai.values_gov_weekly,"
             "ai.values_crisis_gov_live , ai.values_partners_weekly, ai.values_crisis_partners_live,  "
            "ai.values_partners_gov_weekly ,ai.values_crisis_partners_gov_live ,"
            "ai.values_sections, ai.values_sections_live, ai.values_sections_partners, "
            "ai.values_sections_partners_live, ai.values_sections_gov, ai.values_sections_gov_live, ai.values_sections_partners_gov,  "
            "ai.values_sections_partners_gov_live, "
            "a1.master_indicator, a1.master_indicator_sub "
            "FROM public.activityinfo_indicator a1, public.activityinfo_activity aa, "
            "public.activityinfo_indicator_summation_sub_indicators ais, public.activityinfo_indicator ai "
            "WHERE ai.activity_id = aa.id AND a1.id = ais.from_indicator_id AND ais.to_indicator_id = ai.id "
            "AND aa.database_id = %s AND (a1.master_indicator = true or a1.master_indicator_sub = true)",
            [ai_db.id])

    rows = cursor.fetchall()

    for row in rows:
        if row[0] not in rows_data:
            rows_data[row[0]] = {}

        rows_data[row[0]][row[1]] = row

    for indicator in indicators.iterator():
        values_month = {}
        values_partners = {}
        values_gov = {}
        values_partners_gov = {}
        values_sections = {}
        values_sections_partners = {}
        values_sections_gov = {}
        values_sections_partners_gov = {}


        if indicator.id in rows_data:
            indicator_values = rows_data[indicator.id]
            for key, key_values in indicator_values.items():
                sub_indicator_values = indicator_values[key]

                if report_type == 'live':
                    values = sub_indicator_values[3]  # values_live
                    values1 = sub_indicator_values[5]  # values_gov_live
                    values2 = sub_indicator_values[7]  # values_partners_live
                    values3 = sub_indicator_values[9]  # values_partners_gov_live
                    values4 = sub_indicator_values[11]  # values_sections_live
                    values5 = sub_indicator_values[13]  # values_sections_partners_live
                    values6 = sub_indicator_values[15]  # values_sections_gov_live
                    values7 = sub_indicator_values[17]  # values_sections_partners_gov_live

                elif report_type == 'weekly':
                    values = sub_indicator_values[2]  # values_weekly
                    values1 = sub_indicator_values[4]  # values_gov_weekly
                    values2 = sub_indicator_values[6]  # values_partners_weekly
                    values3 = sub_indicator_values[8]  # values_partners_gov_weekly
                    values4 = sub_indicator_values[10]  # values_sections
                    values5 = sub_indicator_values[12]  # values_sections_partners
                    values6 = sub_indicator_values[14]  # values_sections_gov
                    values7 = sub_indicator_values[16]  # values_sections_partners_gov

                for key in values:
                    val = values[key]
                    if key in values_month:
                        val = values_month[key] + val
                    values_month[key] = val

                for key in values1:
                    val = values1[key]
                    if key in values_gov:
                        val = values_gov[key] + val
                    values_gov[key] = val

                for key in values2:
                    val = values2[key]
                    if key in values_partners:
                        val = values_partners[key] + val
                    values_partners[key] = val

                for key in values3:
                    val = values3[key]
                    if key in values_partners_gov:
                        val = values_partners_gov[key] + val
                    values_partners_gov[key] = val

                if values4:
                    for key in values4:
                        val = values4[key]
                        if key in values_sections:
                            val = values_sections[key] + val
                        values_sections[key] = val

                if values5:
                    for key in values5:
                        val = values5[key]
                        if key in values_sections_partners:
                            val = values_sections_partners[key] + val
                        values_sections_partners[key] = val

                if values6:
                    for key in values6:
                        val = values6[key]
                        if key in values_sections_gov:
                            val = values_sections_gov[key] + val
                        values_sections_gov[key] = val

                if values7:
                    for key in values7:
                        val = values7[key]
                        if key in values_sections_partners_gov:
                            val = values_sections_partners_gov[key] + val
                        values_sections_partners_gov[key] = val

                if report_type == 'live':
                    indicator.values_crisis_live = values_month
                    indicator.values_crisis_gov_live = values_gov
                    indicator.values_crisis_partners_live = values_partners
                    indicator.values_crisis_partners_gov_live = values_partners_gov
                    indicator.values_sections_live = values_sections
                    indicator.values_sections_partners_live = values_sections_partners
                    indicator.values_sections_gov_live = values_sections_gov
                    indicator.values_sections_partners_gov_live = values_sections_partners_gov

                elif report_type == 'weekly':
                    indicator.values_weekly = values_month
                    indicator.values_gov_weekly = values_gov
                    indicator.values_partners_weekly = values_partners
                    indicator.values_partners_gov_weekly = values_partners_gov
                    indicator.values_sections = values_sections
                    indicator.values_sections_partners = values_sections_partners
                    indicator.values_sections_gov = values_sections_gov
                    indicator.values_sections_partners_gov = values_sections_partners_gov

            indicator.save()


def calculate_indicators_values_percentage_1(ai_db, report_type=None):
    from django.db import connection
    from internos.activityinfo.models import Indicator

    indicators = Indicator.objects.filter(activity__database__ai_id=ai_db.ai_id,
                                          calculated_indicator=True).only(
        'denominator_indicator',
        'numerator_indicator',
        'denominator_multiplication',
        'values_weekly',
        'values_gov_weekly',
        'values_partners_weekly',
        'values_partners_gov_weekly',
        'values_cumulative_weekly',
        'values_crisis_live',
        'values_crisis_gov_live',
        'values_crisis_partners_live',
        'values_crisis_partners_gov_live',
        'values_crisis_cumulative_live',
        'values_sections',
        'values_sections_partners',
        'values_sections_gov',
        'values_sections_partners_gov',
        'values_sections_live',
        'values_sections_partners_live',
        'values_sections_gov_live',
        'values_sections_partners_gov_live',

    )

    rows_data = {}
    cursor = connection.cursor()
    cursor.execute(
        "SELECT distinct a1.id, a1.calculated_percentage, aa.name, ai.id, ai.values_weekly, ai.values_crisis_live, "
        "ai.values_gov_weekly, ai.values_crisis_gov_live, ai.values_partners_weekly, ai.values_crisis_partners_live, ai.values_partners_gov_weekly, "
        "ai.values_crisis_partners_gov_live , ai.values_sections, ai.values_sections_live, ai.values_sections_partners, "
        "ai.values_sections_partners_live, ai.values_sections_gov, ai.values_sections_gov_live,"
        " ai.values_sections_partners_gov, ai.values_sections_partners_gov_live  "
        "FROM public.activityinfo_indicator a1, public.activityinfo_activity aa, "
        "public.activityinfo_indicator_sub_indicators ais, public.activityinfo_indicator ai "
        "WHERE ai.activity_id = aa.id AND a1.id = ais.from_indicator_id AND ais.to_indicator_id = ai.id "
        "AND aa.database_id = %s AND a1.calculated_indicator = true",
        [ai_db.id])

    rows = cursor.fetchall()
    for row in rows:
        rows_data[row[0]] = row

    for indicator in indicators.iterator():
        values_month = {}
        values_partners = {}
        values_gov = {}
        values_partners_gov = {}
        values_sections = {}
        values_sections_partners = {}
        values_sections_gov = {}
        values_sections_partners_gov = {}

        if indicator.id in rows_data:
            indicator_values = rows_data[indicator.id]
            reporting_level = indicator_values[2]
            calculated_percentage = indicator_values[1]

            if report_type == 'live':
                values = indicator_values[5]  # values_live
                values1 = indicator_values[7]  # values_gov_live
                values2 = indicator_values[9]  # values_partners_live
                values3 = indicator_values[11]  # values_partners_gov_live
                values4 = indicator_values[13]  # values_sections_live
                values5 = indicator_values[15]  # values_sections_partners_live
                values6 = indicator_values[17]  # values_sections_gov_live
                values7 = indicator_values[19]  # values_sections_partners_gov_live

            elif report_type == 'weekly':
                values = indicator_values[4]  # values_weekly
                values1 = indicator_values[6]  # values_gov_weekly
                values2 = indicator_values[8]  # values_partners_weekly
                values3 = indicator_values[10]  # values_partners_gov_weekly
                values4 = indicator_values[12]  # values_sections
                values5 = indicator_values[14]  # values_sections_partners
                values6 = indicator_values[16]  # values_sections_gov
                values7 = indicator_values[18]  # values_sections_partners_gov

            for key in values:
                val = values[key]
                try:
                    if reporting_level == 'Municipality level':
                        values_month[key] = val * calculated_percentage / 100
                    elif reporting_level == 'Site level':
                        values_month[key] = val * calculated_percentage / 100
                except Exception as ex:
                    values_month[key] = 0

            for key in values1:
                val = values1[key]
                try:
                    if reporting_level == 'Municipality level':
                        values_gov[key] = val * calculated_percentage / 100
                    elif reporting_level == 'Site level':
                        values_gov[key] = val * calculated_percentage / 100
                except Exception as ex:
                    values_gov[key] = 0

            for key in values2:
                val = values2[key]
                try:
                    if reporting_level == 'Municipality level':
                        values_partners[key] = val * calculated_percentage / 100
                    elif reporting_level == 'Site level':
                        values_partners[key] = val * calculated_percentage / 100
                except Exception as ex:
                    values_partners[key] = 0

            for key in values3:
                val = values3[key]
                try:
                    if reporting_level == 'Municipality level':
                        values_partners_gov[key] = val * calculated_percentage / 100
                    elif reporting_level == 'Site level':
                        values_partners_gov[key] = val * calculated_percentage / 100
                except Exception as ex:
                    values_partners_gov[key] = 0

            for key in values4:
                val = values4[key]
                try:
                    if reporting_level == 'Municipality level':
                        values_sections[key] = val * calculated_percentage / 100
                    elif reporting_level == 'Site level':
                        values_sections[key] = val * calculated_percentage / 100
                except Exception as ex:
                    values_sections[key] = 0

            for key in values5:
                val = values5[key]
                try:
                    if reporting_level == 'Municipality level':
                        values_sections_partners[key] = val * calculated_percentage / 100
                    elif reporting_level == 'Site level':
                        values_sections_partners[key] = val * calculated_percentage / 100
                except Exception as ex:
                    values_sections_partners[key] = 0

            for key in values6:
                val = values6[key]
                try:
                    if reporting_level == 'Municipality level':
                        values_sections_gov[key] = val * calculated_percentage / 100
                    elif reporting_level == 'Site level':
                        values_sections_gov[key] = val * calculated_percentage / 100
                except Exception as ex:
                    values_sections_gov[key] = 0

            for key in values7:
                val = values7[key]
                try:
                    if reporting_level == 'Municipality level':
                        values_sections_partners_gov[key] = val * calculated_percentage / 100
                    elif reporting_level == 'Site level':
                        values_sections_partners_gov[key] = val * calculated_percentage / 100
                except Exception as ex:
                    values_sections_partners_gov[key] = 0

            if report_type == 'live':
                indicator.values_crisis_live = values_month
                indicator.values_crisis_gov_live = values_gov
                indicator.values_crisis_partners_live = values_partners
                indicator.values_crisis_partners_gov_live = values_partners_gov
                if ai_db.have_sections:
                    indicator.values_sections_live = values_sections
                    indicator.values_sections_partners_live = values_sections_partners
                    indicator.values_sections_gov_live = values_sections_gov
                    indicator.values_sections_partners_gov_live = values_sections_partners_gov

            elif report_type == 'weekly':
                indicator.values_weekly = values_month
                indicator.values_gov_weekly = values_gov
                indicator.values_partners_weekly = values_partners
                indicator.values_partners_gov_weekly = values_partners_gov
                if ai_db.have_sections:
                    indicator.values_sections = values_sections
                    indicator.values_sections_partners = values_sections_partners
                    indicator.values_sections_gov = values_sections_gov
                    indicator.values_sections_partners_gov = values_sections_partners_gov

            indicator.save()


def calculate_master_indicators_values_percentage(ai_db, report_type=None):
    from internos.activityinfo.models import Indicator, ActivityReport, LiveActivityReport

    indicators = Indicator.objects.filter(activity__database__ai_id=ai_db.ai_id,
                                          master_indicator=True,
                                          measurement_type='percentage').only(
        'denominator_indicator',
        'numerator_indicator',
        'denominator_multiplication',
        'values_weekly',
        'values_gov_weekly',
        'values_partners_weekly',
        'values_partners_gov_weekly',
        'values_crisis_live',
        'values_crisis_gov_live',
        'values_crisis_partners_live',
        'values_crisis_partners_gov_live',
        'values_crisis_cumulative_live',
        'values_sections',
        'values_sections_partners',
        'values_sections_gov',
        'values_sections_partners_gov',
        'values_sections_live',
        'values_sections_partners_live',
        'values_sections_gov_live',
        'values_sections_partners_gov_live',
        'values_cumulative_weekly',

    )
    # last_month = int(datetime.datetime.now().strftime("%m")) + 1
    last_month = get_extraction_month(ai_db) + 1

    if report_type == 'live':
        report = LiveActivityReport.objects.filter(database_id=ai_db.ai_id)
    else:
        report = ActivityReport.objects.filter(database_id=ai_db.ai_id)
    if ai_db.is_funded_by_unicef:
        report = report.filter(funded_by='UNICEF')

    report = report.only('partner_id', 'location_adminlevel_governorate_code', 'reporting_section')

    partners = report.values('partner_id').order_by('partner_id').distinct('partner_id')
    governorates = report.values('location_adminlevel_governorate_code').order_by(
        'location_adminlevel_governorate_code').distinct('location_adminlevel_governorate_code')
    governorates1 = report.values('location_adminlevel_governorate_code').order_by(
        'location_adminlevel_governorate_code').distinct('location_adminlevel_governorate_code')
    sections = report.values('reporting_section').distinct()
    # last_month = 13

    for indicator in indicators.iterator():

        try:
            if report_type == 'live':
                denominator = denominator_indicator.values_crisis_cumulative_live['months'] if 'months' in \
                                                                                        denominator_indicator.cumulative_values_live[
                                                                                            'months'] else 0
                numerator = numerator_indicator.values_crisis_cumulative_live['months'] if 'months' in \
                                                                                    numerator_indicator.cumulative_values_live[
                                                                                        'months'] else 0

            elif report_type == 'weekly':
                denominator = denominator_indicator.values_cumulative_weekly['months'] if 'months' in \
                                                                                          denominator_indicator.values_cumulative_weekly[
                                                                                              'months'] else 0
                numerator = numerator_indicator.values_cumulative_weekly['months'] if 'months' in \
                                                                                      numerator_indicator.values_cumulative_weekly[
                                                                                          'months'] else 0
            cumulative_months = numerator / denominator
        except Exception as ex:
            logger.error(ex.message)
            cumulative_months = 0

        for month in range(1, last_month):
            month = str(month)
            values_gov = {}
            values_partners = {}
            values_partners_gov = {}
            values_sections = {}
            values_sections_partners = {}
            values_sections_gov = {}
            values_sections_partners_gov = {}
            denominator_indicator = indicator.denominator_indicator
            numerator_indicator = indicator.numerator_indicator
            if not denominator_indicator or not numerator_indicator:
                continue
            try:
                if report_type == 'live':
                    denominator = denominator_indicator.values_crisis_live[
                        month] if month in denominator_indicator.values_crisis_live else 0
                    numerator = numerator_indicator.values_crisis_live[
                        month] if month in numerator_indicator.values_crisis_live else 0
                elif report_type == 'weekly':
                    denominator = denominator_indicator.values_weekly[
                        month] if month in denominator_indicator.values_weekly else 0
                    numerator = numerator_indicator.values_weekly[month] if month in numerator_indicator.values_weekly else 0

                values_month = numerator / denominator
            except Exception as ex:
                logger.error(ex.message)
                values_month = 0

            for gov1 in governorates1:
                key = "{}-{}".format(month, gov1['location_adminlevel_governorate_code'])
                try:
                    if report_type == 'live':
                        denominator = denominator_indicator.values_crisis_gov_live[
                            key] if key in denominator_indicator.values_crisis_gov_live else 0
                        numerator = numerator_indicator.values_crisis_gov_live[
                            key] if key in numerator_indicator.values_crisis_gov_live else 0
                    elif report_type == 'weekly':
                        denominator = denominator_indicator.values_gov_weekly[
                            key] if key in denominator_indicator.values_gov_weekly else 0
                        numerator = numerator_indicator.values_gov_weekly[
                            key] if key in numerator_indicator.values_gov_weekly else 0

                    values_gov[key] = numerator / denominator
                except Exception as ex:
                    logger.error(ex.message)
                    values_gov[key] = 0

                for section in sections:
                    if 'reporting_section' in section and section['reporting_section']:
                        key3 = "{}-{}-{}".format(month, section['reporting_section'],gov1['location_adminlevel_governorate_code'])

                        try:
                            if report_type == 'live':
                                denominator = denominator_indicator.values_sections_gov_live[
                                    key3] if key3 in denominator_indicator.values_sections_gov_live else 0
                                numerator = numerator_indicator.values_sections_gov_live[
                                    key3] if key3 in numerator_indicator.values_sections_gov_live else 0
                            else:
                                denominator = denominator_indicator.values_sections_gov[
                                    key3] if key3 in denominator_indicator.values_sections_gov else 0
                                numerator = numerator_indicator.values_sections_gov[
                                    key3] if key3 in numerator_indicator.values_sections_gov else 0
                            values_sections_gov[key3] = numerator / denominator
                        except Exception:
                            values_sections_gov[key3] = 0

            for section in sections:
                if 'reporting_section' in section and section['reporting_section']:
                    key4 = "{}-{}".format(month, section['reporting_section'])

                    try:
                        if report_type == 'live':
                            denominator = denominator_indicator.values_sections_live[
                                key4] if key4 in denominator_indicator.values_sections_live else 0
                            numerator = numerator_indicator.values_sections_live[
                                key4] if key4 in numerator_indicator.values_sections_live else 0
                        else:
                            denominator = denominator_indicator.values_sections[
                                key4] if key4 in denominator_indicator.values_sections else 0
                            numerator = numerator_indicator.values_sections[
                                key4] if key4 in numerator_indicator.values_sections else 0
                        values_sections[key4] = numerator / denominator
                    except Exception:
                        values_sections[key4] = 0

            for partner in partners:
                key1 = "{}-{}".format(month, partner['partner_id'])

                try:
                    if report_type == 'live':
                        denominator = denominator_indicator.values_crisis_partners_live[
                            key1] if key1 in denominator_indicator.values_crisis_partners_live else 0
                        numerator = numerator_indicator.values_crisis_partners_live[
                            key1] if key1 in numerator_indicator.values_crisis_partners_live else 0

                    elif report_type == 'weekly':
                        denominator = denominator_indicator.values_partners_weekly[
                            key1] if key1 in denominator_indicator.values_partners_weekly else 0
                        numerator = numerator_indicator.values_partners_weekly[
                            key1] if key1 in numerator_indicator.values_partners_weekly else 0

                    values_partners[key1] = numerator / denominator
                except Exception as ex:
                    logger.error(ex.message)
                    values_partners[key1] = 0

                for gov in governorates:
                    key2 = "{}-{}-{}".format(month, partner['partner_id'], gov['location_adminlevel_governorate_code'])
                    try:
                        if report_type == 'live':
                            denominator = denominator_indicator.values_crisis_partners_gov_live[
                                key2] if key2 in denominator_indicator.values_crisis_partners_gov_live else 0
                            numerator = numerator_indicator.values_crisis_partners_gov_live[
                                key2] if key2 in numerator_indicator.values_crisis_partners_gov_live else 0

                        elif report_type == 'weekly':
                            denominator = denominator_indicator.values_partners_gov_weekly[
                                key2] if key2 in denominator_indicator.values_partners_gov_weekly else 0
                            numerator = numerator_indicator.values_partners_gov_weekly[
                                key2] if key2 in numerator_indicator.values_partners_gov_weekly else 0

                        values_partners_gov[key2] = numerator / denominator
                    except Exception as ex:
                        logger.error(ex.message)
                        values_partners_gov[key2] = 0

                    for section in sections:
                        key5 = "{}-{}-{}-{}".format(month, section['reporting_section'], partner['partner_id'],gov['location_adminlevel_governorate_code'])

                        try:
                            if report_type == 'live':
                                denominator = denominator_indicator.values_sections_partners_gov_live[
                                    key5] if key5 in denominator_indicator.values_sections_partners_gov_live else 0
                                numerator = numerator_indicator.values_sections_partners_gov_live[
                                    key5] if key5 in numerator_indicator.values_sections_partners_gov_live else 0
                            else:
                                denominator = denominator_indicator.values_sections_partners_gov[
                                    key5] if key5 in denominator_indicator.values_sections_partners_gov else 0
                                numerator = numerator_indicator.values_sections_partners_gov[
                                    key5] if key5 in numerator_indicator.values_sections_partners_gov else 0
                            values_sections_partners_gov[key5] = numerator / denominator
                        except Exception:
                            values_sections_partners_gov[key5] = 0

                for section in sections:
                    if 'reporting_section' in section and section['reporting_section']:
                        key6 = "{}-{}-{}".format(month, section['reporting_section'],partner['partner_id'])

                        try:
                            if report_type == 'live':
                                denominator = denominator_indicator.values_sections_partners_live[
                                    key6] if key6 in denominator_indicator.values_sections_partners_live else 0
                                numerator = numerator_indicator.values_sections_partners_live[
                                    key6] if key6 in numerator_indicator.values_sections_partners_live else 0
                            else:
                                denominator = denominator_indicator.values_sections_partners[
                                    key6] if key6 in denominator_indicator.values_sections_partners else 0
                                numerator = numerator_indicator.values_sections_partners[
                                    key6] if key6 in numerator_indicator.values_sections_partners else 0
                            values_sections_partners[key6] = numerator / denominator
                        except Exception:
                            values_sections_partners[key6] = 0

            if report_type == 'live':
                indicator.values_crisis_live[month] = values_month
                indicator.values_crisis_gov_live.update(values_gov)
                indicator.values_crisis_partners_live.update(values_partners)
                indicator.values_crisis_partners_gov_live.update(values_partners_gov)
                if ai_db.have_sections:
                    indicator.values_sections_live.update(values_sections)
                    indicator.values_sections_partners_live.update(values_sections_partners)
                    indicator.values_sections_gov_live.update(values_sections_gov)
                    indicator.values_sections_partners_gov_live.update(values_sections_partners_gov)

            elif report_type == 'weekly':
                indicator.values_weekly[month] = values_month
                indicator.values_gov_weekly.update(values_gov)
                indicator.values_partners_weekly.update(values_partners)
                indicator.values_partners_gov_weekly.update(values_partners_gov)
                if ai_db.have_sections:
                    indicator.values_sections.update(values_sections)
                    indicator.values_sections_partners.update(values_sections_partners)
                    indicator.values_sections_gov.update(values_sections_gov)
                    indicator.values_sections_partners_gov.update(values_sections_partners_gov)

        if report_type == 'live':
            indicator.values_crisis_cumulative_live['months'] = cumulative_months
        elif report_type == 'weekly':
            indicator.values_cumulative_weekly['months'] = cumulative_months

        indicator.save()


def calculate_master_indicators_values_denominator_multiplication(ai_db, report_type=None):
    from internos.activityinfo.models import Indicator, ActivityReport, LiveActivityReport

    indicators = Indicator.objects.filter(activity__database__ai_id=ai_db.ai_id,
                                          master_indicator=True,
                                          measurement_type='percentage_x').only(
        'denominator_indicator',
        'numerator_indicator',
        'denominator_multiplication',
        'values_weekly',
        'values_gov_weekly',
        'values_partners_weekly',
        'values_partners_gov_weekly',
        'values_cumulative_weekly',
        'values_crisis_live',
        'values_crisis_gov_live',
        'values_crisis_partners_live',
        'values_crisis_partners_gov_live',
        'values_crisis_cumulative_live',
        'values_sections',
        'values_sections_partners',
        'values_sections_gov',
        'values_sections_partners_gov',
        'values_sections_live',
        'values_sections_partners_live',
        'values_sections_gov_live',
        'values_sections_partners_gov_live',

    )

    # last_month = int(datetime.datetime.now().strftime("%m")) + 1
    last_month = get_extraction_month(ai_db) + 1

    if report_type == 'live':
        report = LiveActivityReport.objects.filter(database_id=ai_db.ai_id)
    else:
        report = ActivityReport.objects.filter(database_id=ai_db.ai_id)
    if ai_db.is_funded_by_unicef:
        report = report.filter(funded_by='UNICEF')

    report = report.only('partner_id', 'location_adminlevel_governorate_code')

    partners = report.values('partner_id').order_by('partner_id').distinct('partner_id')
    governorates = report.values('location_adminlevel_governorate_code').order_by(
        'location_adminlevel_governorate_code').distinct('location_adminlevel_governorate_code')
    governorates1 = report.values('location_adminlevel_governorate_code').order_by(
        'location_adminlevel_governorate_code').distinct('location_adminlevel_governorate_code')

    sections = report.values('reporting_section').distinct()
    # last_month = 13

    for indicator in indicators.iterator():
        for month in range(1, last_month):
            month = str(month)
            values_gov = {}
            values_partners = {}
            values_partners_gov = {}
            values_sections = {}
            values_sections_partners = {}
            values_sections_gov = {}
            values_sections_partners_gov = {}

            denominator_indicator = indicator.denominator_indicator
            numerator_indicator = indicator.numerator_indicator
            denominator_multiplication = indicator.denominator_multiplication
            if not denominator_indicator or not numerator_indicator:
                continue
            try:
                if report_type == 'live':
                    denominator = denominator_indicator.values_crisis_live[
                        month] if month in denominator_indicator.values_crisis_live else 0
                    numerator = numerator_indicator.values_crisis_live[
                        month] if month in numerator_indicator.values_crisis_live else 0
                elif report_type == 'weekly':
                    denominator = denominator_indicator.values_weekly[
                        month] if month in denominator_indicator.values_weekly else 0
                    numerator = numerator_indicator.values_weekly[
                        month] if month in numerator_indicator.values_weekly else 0

                denominator = denominator * denominator_multiplication
                values_month = numerator / denominator
            except Exception as ex:
                values_month = 0

            for gov1 in governorates1:
                key = "{}-{}".format(month, gov1['location_adminlevel_governorate_code'])
                try:
                    if report_type == 'live':
                        denominator = denominator_indicator.values_crisis_gov_live[
                            key] if key in denominator_indicator.values_crisis_gov_live else 0
                        numerator = numerator_indicator.values_crisis_gov_live[
                            key] if key in numerator_indicator.values_crisis_gov_live else 0

                    elif report_type == 'weekly':
                        denominator = denominator_indicator.values_gov_weekly[
                            key] if key in denominator_indicator.values_gov_weekly else 0
                        numerator = numerator_indicator.values_gov_weekly[
                            key] if key in numerator_indicator.values_gov_weekly else 0

                    values_gov[key] = numerator / denominator
                except Exception:
                    values_gov[key] = 0

            for section in sections:
                if 'reporting_section' in section and section['reporting_section']:
                    key = "{}-{}".format(month, section['reporting_section'])
                    try:
                        if report_type == 'live':
                            denominator = denominator_indicator.values_sections_live[
                                key] if key in denominator_indicator.values_sections_live else 0
                            numerator = numerator_indicator.values_sections_live[
                                key] if key in numerator_indicator.values_sections_live else 0
                        else:
                            denominator = denominator_indicator.values_sections[
                                key] if key in denominator_indicator.values_sections else 0
                            numerator = numerator_indicator.values_sections[key] if key in numerator_indicator.values_sections else 0
                        denominator = denominator * denominator_multiplication
                        values_sections[key] = numerator / denominator
                    except Exception:
                        values_sections[key] = 0

            for partner in partners:
                key1 = "{}-{}".format(month, partner['partner_id'])

                try:
                    if report_type == 'live':
                        denominator = denominator_indicator.values_crisis_partners_live[
                            key1] if key1 in denominator_indicator.values_crisis_partners_live else 0
                        numerator = numerator_indicator.values_crisis_partners_live[
                            key1] if key1 in numerator_indicator.values_crisis_partners_live else 0

                    elif report_type == 'weekly':
                        denominator = denominator_indicator.values_partners_weekly[
                            key1] if key1 in denominator_indicator.values_partners_weekly else 0
                        numerator = numerator_indicator.values_partners_weekly[
                            key1] if key1 in numerator_indicator.values_partners_weekly else 0
                    denominator = denominator * denominator_multiplication
                    values_partners[key1] = numerator / denominator
                except Exception:
                    values_partners[key1] = 0

                for gov in governorates:
                    key2 = "{}-{}-{}".format(month, partner['partner_id'], gov['location_adminlevel_governorate_code'])
                    try:
                        if report_type == 'live':
                            denominator = denominator_indicator.values_crisis_partners_gov_live[
                                key2] if key2 in denominator_indicator.values_crisis_partners_gov_live else 0
                            numerator = numerator_indicator.values_crisis_partners_gov_live[
                                key2] if key2 in numerator_indicator.values_crisis_partners_gov_live else 0

                        elif report_type == 'weekly':
                            denominator = denominator_indicator.values_partners_gov_weekly[
                                key2] if key2 in denominator_indicator.values_partners_gov_weekly else 0
                            numerator = numerator_indicator.values_partners_gov_weekly[
                                key2] if key2 in numerator_indicator.values_partners_gov_weekly else 0

                        denominator = denominator * denominator_multiplication
                        values_partners_gov[key2] = numerator / denominator
                    except Exception:
                        values_partners_gov[key2] = 0

                    for section in sections:
                        key6 = "{}-{}-{}".format(month, section['reporting_section'],
                                                    gov['location_adminlevel_governorate_code'])
                        try:
                            if report_type == 'live':
                                denominator = denominator_indicator.values_sections_gov_live[
                                    key6] if key6 in denominator_indicator.values_sections_gov_live else 0
                                numerator = numerator_indicator.values_sections_gov_live[
                                    key6] if key6 in numerator_indicator.values_sections_gov_live else 0
                            else:
                                denominator = denominator_indicator.values_sections_gov[
                                    key6] if key6 in denominator_indicator.values_sections_gov else 0
                                numerator = numerator_indicator.values_sections_gov[
                                    key6] if key6 in numerator_indicator.values_sections_gov else 0
                            denominator = denominator * denominator_multiplication
                            values_sections_gov[key6] = numerator / denominator
                        except Exception:
                            values_sections_gov[key6] = 0

                    for section in sections:
                        key3 = "{}-{}-{}-{}".format(month, section['reporting_section'], partner['partner_id'],gov['location_adminlevel_governorate_code'])
                        try:
                            if report_type == 'live':
                                denominator = denominator_indicator.values_sections_partners_gov_live[
                                    key3] if key3 in denominator_indicator.values_sections_partners_gov_live else 0
                                numerator = numerator_indicator.values_sections_partners_gov_live[
                                    key3] if key3 in numerator_indicator.values_sections_partners_gov_live else 0
                            else:
                                denominator = denominator_indicator.values_sections_partners_gov[
                                    key3] if key3 in denominator_indicator.values_sections_partners_gov else 0
                                numerator = numerator_indicator.values_sections_partners_gov[
                                    key3] if key3 in numerator_indicator.values_sections_partners_gov else 0
                            denominator = denominator * denominator_multiplication
                            values_sections_partners_gov[key3] = numerator / denominator
                        except Exception:
                            values_sections_partners_gov[key3] = 0

                for section in sections:
                    if 'reporting_section' in section and section['reporting_section']:
                        key4 = "{}-{}-{}".format(month, section['reporting_section'],partner['partner_id'])
                        try:
                            if report_type == 'live':
                                denominator = denominator_indicator.values_sections_partners_live[
                                    key4] if key4 in denominator_indicator.values_sections_partners_live else 0
                                numerator = numerator_indicator.values_sections_partners_live[
                                    key4] if key4 in numerator_indicator.values_sections_partners_live else 0
                            else:
                                denominator = denominator_indicator.values_sections_partners[
                                    key4] if key4 in denominator_indicator.values_sections_partners else 0
                                numerator = numerator_indicator.values_sections_partners[
                                    key4] if key4 in numerator_indicator.values_sections_partners else 0
                            denominator = denominator * denominator_multiplication
                            values_sections_partners[key4] = numerator / denominator
                        except Exception:
                            values_sections_partners[key4] = 0

            if report_type == 'live':
                indicator.values_live[month] = values_month
                indicator.values_gov_live.update(values_gov)
                indicator.values_partners_live.update(values_partners)
                indicator.values_partners_gov_live.update(values_partners_gov)
                if ai_db.have_sections:
                    indicator.values_sections_live.update(values_sections)
                    indicator.values_sections_partners_live.update(values_sections_partners)
                    indicator.values_sections_gov_live.update(values_sections_gov)
                    indicator.values_sections_partners_gov_live.update(values_sections_partners_gov)
            elif report_type == 'weekly':
                # if month == reporting_month:
                #     indicator.values_hpm[reporting_month] = values_month
                indicator.values_weekly[month] = values_month
                indicator.values_gov_weekly.update(values_gov)
                indicator.values_partners_weekly.update(values_partners)
                indicator.values_partners_gov_weekly.update(values_partners_gov)
                if ai_db.have_sections:
                    indicator.values_sections.update(values_sections)
                    indicator.values_sections_partners.update(values_sections_partners)
                    indicator.values_sections_gov.update(values_sections_gov)
                    indicator.values_sections_partners_gov.update(values_sections_partners_gov)

        indicator.save()


def calculate_individual_indicators_values_2(ai_db):
    from django.db import connection
    from internos.activityinfo.models import Indicator

    last_month = int(datetime.datetime.now().strftime("%m")) + 1
    last_month = get_extraction_month(ai_db) + 1
    # last_month = 13

    ai_id = str(ai_db.ai_id)
    indicators = Indicator.objects.filter(activity__database__ai_id=ai_db.ai_id).exclude(master_indicator=True) \
        .exclude(master_indicator_sub=True).only(
        'ai_indicator',
        'values_sections_live',
        'values_sections_partners_live',
        'values_sections_gov_live',
        'values_sections_partners_gov_live',
        'values_crisis_live',
        'values_crisis_gov_live',
        'values_crisis_partners_live',
        'values_crisis_partners_gov_live',
        'values_crisis_cumulative_live'
    )

    rows_months = {}
    rows_partners = {}
    rows_govs = {}
    rows_partners_govs = {}
    rows_sections = {}
    rows_sections_partners = {}
    rows_sections_gov = {}
    rows_sections_partners_gov = {}

    cursor = connection.cursor()
    covid_condition = ""

    if ai_db.support_covid :
        covid_condition = "AND support_covid = true "

    funded_condition = ""

    if ai_db.is_funded_by_unicef:
        funded_condition = "AND funded_by = 'UNICEF' "

    query_condition = " WHERE date_part('month', start_date) = %s AND database_id = %s " + funded_condition + covid_condition

    for month in range(1, last_month):
        month = str(month)
        cursor.execute("SELECT indicator_id, SUM(indicator_value) as indicator_value "
                       "FROM activityinfo_liveactivityreport "
                       + query_condition +
                       " GROUP BY indicator_id", [month, ai_id])
        rows = cursor.fetchall()

        for row in rows:
            if row[0] not in rows_months:
                rows_months[row[0]] = {}
            rows_months[row[0]][month] = row[1]

        cursor.execute(
            "SELECT indicator_id, SUM(indicator_value) as indicator_value, location_adminlevel_governorate_code"
            " FROM activityinfo_liveactivityreport "
            + query_condition +
            "GROUP BY indicator_id, location_adminlevel_governorate_code", [month, ai_id])

        rows = cursor.fetchall()

        for row in rows:
            if row[0] not in rows_govs:
                rows_govs[row[0]] = {}
            key = "{}-{}".format(month, row[2])
            rows_govs[row[0]][key] = row[1]

        cursor.execute(
            "SELECT indicator_id, SUM(indicator_value) as indicator_value, partner_id "
            "FROM activityinfo_liveactivityreport "
            + query_condition +
            "GROUP BY indicator_id, partner_id",
            [month, ai_id])

        rows = cursor.fetchall()

        for row in rows:
            if row[0] not in rows_partners:
                rows_partners[row[0]] = {}
            key = "{}-{}".format(month, row[2])
            rows_partners[row[0]][key] = row[1]

        cursor.execute(
            "SELECT indicator_id, SUM(indicator_value) as indicator_value, location_adminlevel_governorate_code, partner_id "
            "FROM activityinfo_liveactivityreport "
            + query_condition +
            "GROUP BY indicator_id, location_adminlevel_governorate_code, partner_id",
            [month, ai_id])

        rows = cursor.fetchall()
        for row in rows:
            if row[0] not in rows_partners_govs:
                rows_partners_govs[row[0]] = {}
            key = "{}-{}-{}".format(month, row[2], row[3])
            rows_partners_govs[row[0]][key] = row[1]

        if ai_db.have_sections:
            cursor.execute(
                "SELECT indicator_id, SUM(indicator_value) as indicator_value, reporting_section "
                "FROM activityinfo_liveactivityreport "
                + query_condition +
                "GROUP BY indicator_id, reporting_section",
                [month, ai_id])

            rows = cursor.fetchall()
            for row in rows:
                if row[0] not in rows_sections:
                    rows_sections[row[0]] = {}
                key = "{}-{}".format(month, row[2])
                rows_sections[row[0]][key] = row[1]

            cursor.execute(
                "SELECT indicator_id, SUM(indicator_value) as indicator_value, reporting_section ,partner_id "
                "FROM activityinfo_liveactivityreport "
                + query_condition +
                "GROUP BY indicator_id, reporting_section ,partner_id",
                [month, ai_id])

            rows = cursor.fetchall()
            for row in rows:
                if row[0] not in rows_sections_partners:
                    rows_sections_partners[row[0]] = {}
                key = "{}-{}-{}".format(month, row[2], row[3])
                rows_sections_partners[row[0]][key] = row[1]

            cursor.execute(
                "SELECT indicator_id, SUM(indicator_value) as indicator_value, reporting_section, "
                "location_adminlevel_governorate_code "
                "FROM activityinfo_activityreport "
                + query_condition +
                "GROUP BY indicator_id, reporting_section ,location_adminlevel_governorate_code",
                [month, ai_id])

            rows = cursor.fetchall()
            for row in rows:
                if row[0] not in rows_sections_gov:
                    rows_sections_gov[row[0]] = {}
                key = "{}-{}-{}".format(month, row[2], row[3])
                rows_sections_gov[row[0]][key] = row[1]

            cursor.execute(
                "SELECT indicator_id, SUM(indicator_value) as indicator_value, reporting_section, "
                "location_adminlevel_governorate_code, partner_id "
                "FROM activityinfo_activityreport "
                + query_condition +
                "GROUP BY indicator_id, reporting_section , partner_id ,location_adminlevel_governorate_code",
                [month, ai_id])

            rows = cursor.fetchall()
            for row in rows:
                if row[0] not in rows_sections_partners_gov:
                    rows_sections_partners_gov[row[0]] = {}
                key = "{}-{}-{}-{}".format(month, row[2], row[3], row[4])
                rows_sections_partners_gov[row[0]][key] = row[1]

    for indicator in indicators.iterator():
        if indicator.ai_indicator in rows_months:
            indicator.values_crisis_live = rows_months[indicator.ai_indicator]

        if indicator.ai_indicator in rows_partners:
            indicator.values_crisis_partners_live = rows_partners[indicator.ai_indicator]

        if indicator.ai_indicator in rows_govs:
            indicator.values_crisis_gov_live = rows_govs[indicator.ai_indicator]

        if indicator.ai_indicator in rows_partners_govs:
            indicator.values_crisis_partners_gov_live = rows_partners_govs[indicator.ai_indicator]

        if indicator.ai_indicator in rows_sections:
            if not ai_db.support_covid :
                indicator.values_sections_live = rows_sections[indicator.ai_indicator]

        if indicator.ai_indicator in rows_sections_gov:
            if not ai_db.support_covid:
                indicator.values_sections_gov_live = rows_sections_gov[indicator.ai_indicator]

        if indicator.ai_indicator in rows_sections_partners:
            if not ai_db.support_covid:
                indicator.values_sections_partners_live = rows_sections_partners[indicator.ai_indicator]

        if indicator.ai_indicator in rows_sections_partners_gov:
            if not ai_db.support_covid:
                indicator.values_sections_partners_gov_live = rows_sections_partners_gov[indicator.ai_indicator]

        indicator.save()


def calculate_indicators_status(database):
    from internos.activityinfo.models import Indicator

    year_days = 365
    today = datetime.datetime.now()
    reporting_year = database.reporting_year
    beginning_year = datetime.datetime(int(reporting_year.year), 01, 01)
    # datetime.datetime(int(reporting_year.name), 01, 01)
    delta = today - beginning_year
    total_days = delta.days + 1
    days_passed_per = (total_days * 100) / year_days

    indicators = Indicator.objects.filter(activity__database__ai_id=database.ai_id)

    for indicator in indicators:
        cumulative_per = indicator.cumulative_per
        off_track = days_passed_per - 10
        over_target = days_passed_per + 10
        if cumulative_per < off_track:
            indicator.status = 'Off Track'
            indicator.status_color = 'badge-danger'
        elif cumulative_per > over_target:
            indicator.status = 'Over Track'
            indicator.status_color = 'badge-warning'
        else:
            indicator.status = 'On Track'
            indicator.status_color = 'badge-success'

        cumulative_per = indicator.cumulative_per_sector
        off_track = days_passed_per - 10
        over_target = days_passed_per + 10
        if cumulative_per < off_track:
            indicator.status_sector = 'Off Track'
            indicator.status_color_sector = 'badge-danger'
        elif cumulative_per > over_target:
            indicator.status_sector = 'Over Track'
            indicator.status_color_sector = 'badge-warning'
        else:
            indicator.status_sector = 'On Track'
            indicator.status_color_sector = 'badge-success'

        indicator.save()

    return indicators.count()


def calculate_master_imported_indicators(ai_db,report_type):
    from django.db import connection

    master_indicators = Indicator.objects.filter(activity__database=ai_db).\
        filter(Q(second_activity__isnull=False) | Q(third_activity__isnull=False)).only(
        'id',
        'values_weekly',
        'values_gov_weekly',
        'values_partners_weekly',
        'values_partners_gov_weekly',
        'values_crisis_live',
        'values_crisis_gov_live',
        'values_crisis_partners_live',
        'values_crisis_partners_gov_live',
    )
    if not master_indicators.count():
        return False

    rows_data = {}
    linked_indicators = []

    for ind in master_indicators:
        value = ind.id
        linked_indicators.append(value)

    ids_condition = ', '.join((str(n) for n in linked_indicators))

    cursor = connection.cursor()
    cursor.execute("SELECT distinct a1.id, ai.id, ai.values, ai.values_gov, ai.values_partners, ai.values_partners_gov, "
                   "ai.values_weekly, ai.values_gov_weekly, ai.values_partners_weekly, ai.values_partners_gov_weekly, "
                   "ai.values_crisis_live,ai.values_crisis_gov_live, ai.values_crisis_partners_live, ai.values_crisis_partners_gov_live "
                   "FROM public.activityinfo_indicator ai, public.activityinfo_indicator_summation_sub_indicators ais, public.activityinfo_indicator a1 "
                   "WHERE ai.id = ais.to_indicator_id and ais.from_indicator_id = a1.id "
                   "and a1.id in ("+ids_condition+")")

    rows = cursor.fetchall()

    for row in rows:
        if row[0] not in rows_data:
            rows_data[row[0]] = {}

        rows_data[row[0]][row[1]] = row

    for indicator in master_indicators.iterator():
        values_month = {}
        values_partners = {}
        values_gov = {}
        values_partners_gov = {}

        if indicator.id in rows_data:
            indicator_values = rows_data[indicator.id]
            for key, key_values in indicator_values.items():
                sub_indicator_values = indicator_values[key]

                # values = sub_indicator_values[2] if sub_indicator_values[2] else sub_indicator_values[6]  # values_weekly
                # values1 = sub_indicator_values[3] if sub_indicator_values[3] else sub_indicator_values[7]  # values_gov_weekly
                # values2 = sub_indicator_values[4] if sub_indicator_values[4] else sub_indicator_values[8]  # values_partners_weekly
                # values3 = sub_indicator_values[5] if sub_indicator_values[5] else sub_indicator_values[9]  # values_partners_gov_weekly

                if report_type == 'live':
                    values = sub_indicator_values[10]  # values_weekly
                    values1 = sub_indicator_values[11]  # values_gov_weekly
                    values2 = sub_indicator_values[12]  # values_partners_weekly
                    values3 = sub_indicator_values[13]  # values_partners_gov_weekly
                else:

                    values = sub_indicator_values[6]  # values_weekly
                    values1 = sub_indicator_values[7]  # values_gov_weekly
                    values2 = sub_indicator_values[8]  # values_partners_weekly
                    values3 = sub_indicator_values[9]  # values_partners_gov_weekly

                for key in values:
                    val = values[key]
                    if key in values_month:
                        val = values_month[key] + val
                    values_month[key] = val

                for key in values1:
                    val = values1[key]
                    if key in values_gov:
                        val = values_gov[key] + val
                    values_gov[key] = val

                for key in values2:
                    val = values2[key]
                    if key in values_partners:
                        val = values_partners[key] + val
                    values_partners[key] = val

                for key in values3:
                    val = values3[key]
                    if key in values_partners_gov:
                        val = values_partners_gov[key] + val
                    values_partners_gov[key] = val
                if report_type == 'live':

                    indicator.values_crisis_live = values_month
                    indicator.values_crisis_gov_live = values_gov
                    indicator.values_crisis_partners_live = values_partners
                    indicator.values_crisis_partners_gov_live = values_partners_gov
                else:

                    indicator.values_weekly = values_month
                    indicator.values_gov_weekly = values_gov
                    indicator.values_partners_weekly = values_partners
                    indicator.values_partners_gov_weekly = values_partners_gov

                indicator.save()


def get_partners_list(ai_db, sections=None, govs=None, months=None, report_type=None):
    from django.db import connection

    result = {}
    cursor = connection.cursor()
    where_condition = ""
    funded_condition = ""

    if ai_db.is_funded_by_unicef:
        funded_condition = " AND funded_by = 'UNICEF' "
    if govs:
        where_condition = " and location_adminlevel_governorate_code in (" + govs + ")"

    if sections:
        section_list = ", ".join("'" + str(n) + "'" for n in sections)
        where_condition += " AND reporting_section in (" + section_list + ")"

    if months:
        where_condition += " AND date_part('month', start_date) in (" + months + ")"

    query_condition = "{}'{}'".format(" WHERE database_id =", str(ai_db.ai_id)) + funded_condition + where_condition

    if report_type == 'live':
        cursor.execute(
                "SELECT DISTINCT partner_id, partner_label "
                "FROM activityinfo_liveactivityreport "
                 + query_condition)
    else:
        cursor.execute(
                "SELECT DISTINCT partner_id, partner_label "
                "FROM activityinfo_activityreport "
                + query_condition )

    rows = cursor.fetchall()

    for row in rows:
        result[row[0]] = {
            'partner_id': row[0],
            'partner_label': row[1]
        }

    return result.values()


def get_governorates_list(ai_db, sections=None, partners=None, months=None, report_type=None):
    from django.db import connection

    result = {}
    cursor = connection.cursor()
    where_condition = ""
    funded_condition=""

    if ai_db.is_funded_by_unicef:
        funded_condition = " AND funded_by = 'UNICEF' "

    if sections:
        section_list = ", ".join("'" + str(n) + "'" for n in sections)
        where_condition += " AND reporting_section in (" + section_list + ")"
    if partners:
        partners_list = ", ".join("'" + str(n)+ "'" for n in partners)
        where_condition += " AND partner_id in (" + partners_list + ")"
    if months:
        where_condition += " AND date_part('month', start_date) in (" + months +")"

    query_condition = "{}'{}'".format(" WHERE database_id =", str(ai_db.ai_id)) + funded_condition + where_condition

    if report_type == 'live':
        cursor.execute(
                "SELECT DISTINCT location_adminlevel_governorate_code, location_adminlevel_governorate "
                "FROM activityinfo_liveactivityreport "
                 + query_condition)
    else :
        cursor.execute(
                "SELECT DISTINCT location_adminlevel_governorate_code, location_adminlevel_governorate "
                "FROM activityinfo_activityreport "
                 + query_condition)

    rows = cursor.fetchall()

    for row in rows:
        result[row[0]] = {
            'location_adminlevel_governorate_code': row[0],
            'location_adminlevel_governorate': row[1]
        }

    return result.values()


def get_cadastrals_list(ai_db, report_type=None):
    from django.db import connection

    result = {}
    cursor = connection.cursor()

    if report_type == 'live':

        if ai_db.is_funded_by_unicef:
            cursor.execute(
                "SELECT DISTINCT location_adminlevel_cadastral_area_code, location_adminlevel_cadastral_area "
                "FROM activityinfo_liveactivityreport "
                "WHERE database_id = %s AND funded_by = %s ",
                [str(ai_db.ai_id), 'UNICEF'])
        else:
            cursor.execute(
                "SELECT DISTINCT location_adminlevel_cadastral_area_code, location_adminlevel_cadastral_area "
                "FROM activityinfo_liveactivityreport "
                "WHERE database_id = %s ",
                [str(ai_db.ai_id)])
    else :
        if ai_db.is_funded_by_unicef:
            cursor.execute(
                "SELECT DISTINCT location_adminlevel_cadastral_area_code, location_adminlevel_cadastral_area "
                "FROM activityinfo_activityreport "
                "WHERE database_id = %s AND funded_by = %s ",
                [str(ai_db.ai_id), 'UNICEF'])
        else:
            cursor.execute(
                "SELECT DISTINCT location_adminlevel_cadastral_area_code, location_adminlevel_cadastral_area "
                "FROM activityinfo_activityreport "
                "WHERE database_id = %s ",
                [str(ai_db.ai_id)])

    rows = cursor.fetchall()

    for row in rows:
        result[row[0]] = {
            'location_adminlevel_cadastral_area_code': row[0],
            'location_adminlevel_cadastral_area': row[1]
        }

    return result.values()


def get_reporting_sections_list(ai_db,partners=None, govs=None,months=None, report_type=None):
    from django.db import connection

    result = {}
    cursor = connection.cursor()
    where_condition = ""
    funded_condition = ""

    if ai_db.is_funded_by_unicef:
        funded_condition = " AND funded_by = 'UNICEF' "

    if partners:
        partners_list = ", ".join("'" + str(n) + "'" for n in partners)
        where_condition += " AND partner_id in (" + partners_list + ")"
    if govs:
        where_condition = " and location_adminlevel_governorate_code in (" + govs + ")"
    if months:
        where_condition += " AND date_part('month', start_date) in (" + months + ")"

    query_condition = "{}'{}'".format(" WHERE database_id =", str(ai_db.ai_id)) + funded_condition + where_condition
    if report_type == 'live':
        cursor.execute(
                "SELECT DISTINCT reporting_section "
                "FROM activityinfo_liveactivityreport " + query_condition)
    else:
        cursor.execute(
                "SELECT DISTINCT reporting_section "
                "FROM activityinfo_activityreport "+query_condition
              )
    rows = cursor.fetchall()

    for row in rows:
        result[row[0]] = {
            'reporting_section': row[0],
        }

    return result.values()
