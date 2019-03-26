import os
import csv
import json
import datetime
import subprocess
from django.db.models import Sum, Q
from django.conf import settings


def r_script_command_line(script_name, ai_db):
    command = 'Rscript'
    # path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.dirname(__file__)
    path2script = os.path.join(path, 'RScripts')
    path2script = os.path.join(path2script, script_name)
    print(path2script)

    cmd = [command, path2script, ai_db.username, ai_db.password, str(ai_db.ai_id)]

    try:
        subprocess.check_output(cmd, universal_newlines=True)
    except subprocess.CalledProcessError as e:
        print("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
        return 0

    return 1


def read_data_from_file(ai_id, forced=False, report_type=None):
    from internos.activityinfo.models import Database, ActivityReport, ActivityReportLive
    # from internos.backends.models import ImportLog
    # month_name = datetime.datetime.now().strftime("%B")

    if report_type == 'live':
        model = ActivityReportLive.objects.none()
        ActivityReportLive.objects.filter(database_id=ai_id).delete()
        return add_rows(ai_id=ai_id, model=model)

    if forced:
        model = ActivityReport.objects.none()
        ActivityReport.objects.filter(database_id=ai_id).delete()
        return add_rows(ai_id=ai_id, model=model)

    # try:
    #     ImportLog.objects.get(
    #         object_id=ai_id,
    #         object_type='AI',
    #         month=month_name,
    #         status=True)
    #     return update_rows(ai_id)
    # except ImportLog.DoesNotExist:
    #     ImportLog.objects.create(
    #         object_id=ai_id,
    #         object_name=Database.objects.get(ai_id=ai_id).name,
    #         object_type='AI',
    #         month=month_name,
    #         status=True)
    #     return add_rows(ai_id=ai_id, model=model)


def import_data_via_r_script(ai_db, report_type=None):
    r_script_command_line('ai_generate_excel.R', ai_db)
    total = read_data_from_file(ai_db.ai_id, True, report_type)
    return total


def get_awp_code(name):
    try:
        if '_' in name:
            awp_code = name[:name.find('_')]
        elif ' - ' in name:
            awp_code = name[:name.find(' - ')]
            # ai_indicator.awp_code = name[re.search('\d', name).start():name.find(':')]
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


def set_tags(indicator, tags):
    for tag in tags:
        if tag.name in indicator.name:
            setattr(indicator, tag.tag_field, tag)
        # else:
        #     setattr(indicator, tag.tag_field, None)
    indicator.save()


def clean_string(value, string):
    return value.replace(string, '')


def add_rows(ai_id=None, model=None):

    month = int(datetime.datetime.now().strftime("%m"))
    month_name = datetime.datetime.now().strftime("%B")
    path = os.path.dirname(os.path.abspath(__file__))
    path2file = path+'/AIReports/'+str(ai_id)+'_ai_data.csv'
    ctr = 0

    if not os.path.isfile(path2file):
        return False

    with open(path2file) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            ctr += 1
            indicator_value = 0
            if 'indicator.value' in row:
                indicator_value = row['indicator.value']

            try:
                indicator_value = float(indicator_value)
            except Exception:
                indicator_value = 0

            model.create(
                month=month,
                database=row['database'],
                site_id=row['site.id'],
                report_id=row['report.id'],
                database_id=row['database.id'],
                partner_id=row['partner.id'],
                indicator_id=clean_string(row['indicator.id'], 'i'),
                indicator_name=unicode(row['indicator.name'], errors='replace'),
                indicator_awp_code=get_awp_code(unicode(row['indicator.name'], errors='replace')),
                month_name=month_name,
                partner_label=unicode(row['partner.label'], errors='replace') if 'partner.label' in row else '',
                location_adminlevel_caza_code=row[
                    'location.adminlevel.caza.code'] if 'location.adminlevel.caza.code' in row else '',
                location_adminlevel_caza=unicode(row['location.adminlevel.caza'],
                                                 errors='replace') if 'location.adminlevel.caza' in row else '',
                partner_description=unicode(row['partner.description'],
                                            errors='replace') if 'partner.description' in row else '',
                form=unicode(row['form'], errors='replace') if 'form' in row else '',
                governorate=row['Governorate'] if 'Governorate' in row else '',
                location_longitude=row['location.longitude'] if 'location.longitude' in row else '',
                form_category=row['form.category'] if 'form.category' in row else '',
                indicator_units=row['indicator.units'] if 'indicator.units' in row else '',
                project_description=unicode(row['project.description'],
                                            errors='replace') if 'project.description' in row else '',
                location_adminlevel_cadastral_area_code=row[
                    'location.adminlevel.cadastral_area.code'] if 'location.adminlevel.cadastral_area.code' in row else '',
                location_name=unicode(row['location.name'], errors='replace') if 'location.name' in row else '',
                project_label=unicode(row['project.label'], errors='replace') if 'project.label' in row else '',
                location_adminlevel_governorate_code=row[
                    'location.adminlevel.governorate.code'] if 'location.adminlevel.governorate.code' in row else '',
                end_date=row['end_date'] if 'end_date' in row else '',
                lcrp_appeal=row['LCRP Appeal'] if 'LCRP Appeal' in row else '',
                indicator_value=indicator_value,
                funded_by=row['Funded_by'] if 'Funded_by' in row else '',
                location_latitude=row['location.latitude'] if 'location.latitude' in row else '',
                indicator_category=row['indicator.category'] if 'indicator.category' in row else '',
                location_alternate_name=row[
                    'location.alternate_name'] if 'location.alternate_name' in row else '',
                start_date=row['start_date'] if 'start_date' in row and not row['start_date'] == 'NA' else None,
                location_adminlevel_cadastral_area=unicode(row['location.adminlevel.cadastral_area'],
                                                           errors='replace') if 'location.adminlevel.cadastral_area' in row else '',
                location_adminlevel_governorate=unicode(row[
                    'location.adminlevel.governorate'], errors='replace') if 'location.adminlevel.governorate' in row else '',
            )
    return ctr


def update_rows(ai_id):
    from internos.activityinfo.models import ActivityReport
    path = os.path.dirname(os.path.abspath(__file__))
    path2file = path+'/AIReports/'+str(ai_id)+'_ai_data.csv'

    with open(path2file) as csvfile:
        reader = csv.DictReader(csvfile)
        ctr = 0
        for row in reader:
            ctr += 1
            ActivityReport.objects.update(
                database_id=ai_id,
                indicator_id=clean_string(row['indicator.id'], 'i'),
                indicator_units=row['indicator.units'] if 'indicator.units' in row else '',
                indicator_value=row['indicator.value'] if 'indicator.value' in row else '',
            )
        return ctr


def generate_indicator_awp_code(ai_id):
    from internos.activityinfo.models import Indicator

    data = Indicator.objects.filter(activity__database__ai_id=ai_id)
    ctr = data.count()
    for item in data:
        item.awp_code = get_awp_code(item.name)
        item.save()

    return ctr


def generate_indicator_tag(ai_id):
    from internos.activityinfo.models import Indicator, IndicatorTag

    data = Indicator.objects.filter(activity__database__ai_id=ai_id)
    tags = IndicatorTag.objects.all()

    ctr = data.count()
    for item in data:
        set_tags(item, tags)

    return ctr


def generate_indicator_awp_code2(ai_id):
    from internos.activityinfo.models import ActivityReport

    data = ActivityReport.objects.filter(database_id=ai_id)
    ctr = data.count()
    for item in data:
        item.indicator_awp_code = get_awp_code(item.indicator_name)
        item.save()

    return ctr


def calculate_sum_target(ai_id):
    from internos.activityinfo.models import Indicator

    top_indicators = Indicator.objects.filter(master_indicator=True, activity__database_id=ai_id)
    sub_indicators = Indicator.objects.filter(master_indicator_sub=True, activity__database_id=ai_id)

    for item in sub_indicators:
        if not item.summation_sub_indicators.count():
            continue
        target_sum = item.summation_sub_indicators.exclude(master_indicator=True).aggregate(Sum('target'))
        item.target = target_sum['target__sum'] if target_sum['target__sum'] else 0
        item.save()

    for item in top_indicators:
        # if top_indicators.measurement_type == 'percentage':
        #     try:
        #         item.target = item.denominator_indicator.target / item.numerator_indicator.target
        #     except Exception:
        #         item.target = 0
        # else:
        target_sum = item.summation_sub_indicators.exclude(master_indicator_sub=False,
                                                           master_indicator=False).aggregate(Sum('target'))
        item.target = target_sum['target__sum'] if target_sum['target__sum'] else 0

        item.save()

    return top_indicators.count() + sub_indicators.count()


def link_indicators_data(ai_db, report_type=None):
    result = link_indicators_activity_report(ai_db, report_type)
    # link_ai_partners(report_type)
    # link_etools_partners()

    return result


def link_indicators_activity_report(ai_db, report_type=None):
    from internos.activityinfo.models import Indicator, ActivityReport, ActivityReportLive

    ctr = 0
    if report_type == 'live':
        reports = ActivityReportLive.objects.filter(database_id=ai_db.ai_id)
    else:
        reports = ActivityReport.objects.filter(database_id=ai_db.ai_id)

    reports = reports.exclude(ai_indicator__isnull=False)

    if ai_db.is_funded_by_unicef:
        reports = reports.filter(funded_by='UNICEF')

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
        ai_values.update(ai_indicator_id=item.id)

    return ctr


def link_ai_partners(report_type=None):
    from internos.activityinfo.models import Partner, ActivityReport, ActivityReportLive

    ctr = 0
    if report_type == 'live':
        reports = ActivityReportLive.objects.all()
    else:
        reports = ActivityReport.objects.all()

    partners = Partner.objects.all()

    for item in partners:
        ai_values = reports.filter(partner_id=item.ai_number)
        if not ai_values.count():
            continue
        ctr += ai_values.count()
        ai_values.update(partner_ai_id=item.id)
        item.number = item.ai_number
        item.save()

    return ctr


def link_etools_partners():
    from internos.activityinfo.models import Partner
    from internos.etools.models import PartnerOrganization

    partners = PartnerOrganization.objects.all()

    for partner in partners:
        ai_partners = Partner.objects.filter(Q(name=partner.short_name) |
                                             Q(name=partner.name.upper()) |
                                             Q(name=partner.short_name.upper()) |
                                             Q(full_name=partner.short_name) |
                                             Q(name=partner.name) |
                                             Q(full_name=partner.name))
        if not ai_partners.count():
            continue

        ai_partners.update(partner_etools=partner)


def reset_indicators_values(ai_id, report_type=None):
    from internos.activityinfo.models import Indicator

    indicators = Indicator.objects.filter(activity__database__ai_id=ai_id)
    for indicator in indicators:
        if report_type == 'live':
            indicator.values_live = {}
            indicator.values_gov_live = {}
            indicator.values_partners_live = {}
            indicator.values_partners_gov_live = {}
            indicator.cumulative_values_live = {}
        else:
            indicator.values = {}
            indicator.values_gov = {}
            indicator.values_partners = {}
            indicator.values_partners_gov = {}
            indicator.cumulative_values = {}
        indicator.save()

    return indicators.count()


def calculate_indicators_values(ai_db, report_type=None):
    reset_indicators_values(ai_db.ai_id, report_type)
    calculate_individual_indicators_values(ai_db, report_type)
    calculate_master_indicators_values(ai_db, report_type, True)
    calculate_master_indicators_values(ai_db, report_type)
    calculate_master_indicators_values_percentage(ai_db, report_type)
    calculate_master_indicators_values_denominator_multiplication(ai_db, report_type)
    calculate_indicators_values_percentage(ai_db, report_type)
    calculate_indicators_cumulative_results(ai_db, report_type)
    calculate_indicators_status(ai_db)

    return 0


def calculate_indicators_cumulative_results(ai_db, report_type=None):
    from internos.activityinfo.models import Indicator, ActivityReport, ActivityReportLive

    indicators = Indicator.objects.filter(activity__database__ai_id=ai_db.ai_id)

    if report_type == 'live':
        report = ActivityReportLive.objects.filter(database=ai_db)
    else:
        report = ActivityReport.objects.filter(database=ai_db)

    if ai_db.is_funded_by_unicef:
        report = report.filter(funded_by__contains='UNICEF')

    partners = report.values('partner_id').distinct()
    governorates = report.values('location_adminlevel_governorate_code').distinct()

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
                c_value += float(values[str(c_month)])
                cum_month[str(month)] = c_value

            for partner in partners:
                key = '{}-{}'.format(month, partner['partner_id'])
                if key in values_partners:
                    cum_partner[partner['partner_id']] = values_partners[key] + (cum_partner[partner['partner_id']] if partner['partner_id'] in cum_partner else 0)

            for gov in governorates:
                key = '{}-{}'.format(month, gov['location_adminlevel_governorate_code'])
                if key in values_govs:
                    cum_gov[gov['location_adminlevel_governorate_code']] = values_govs[key] + (cum_gov[gov['location_adminlevel_governorate_code']] if gov['location_adminlevel_governorate_code'] in cum_gov else 0)

                for partner in partners:
                    key = '{}-{}-{}'.format(month, partner['partner_id'], gov['location_adminlevel_governorate_code'])
                    key_c = '{}-{}'.format(partner['partner_id'], gov['location_adminlevel_governorate_code'])
                    if key in values_partners_govs:
                        cum_partner_gov[key_c] = values_partners_govs[key] + (cum_partner_gov[key_c] if key_c in cum_partner_gov else 0)

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


def reset_hpm_indicators_values(ai_id):
    from internos.activityinfo.models import Indicator

    indicators = Indicator.objects.filter(activity__database__ai_id=ai_id)
    for indicator in indicators:
        indicator.values_hpm = {}
        indicator.cumulative_values_hpm = {}
        indicator.save()

    return indicators.count()


def calculate_indicators_cumulative_hpm(ai_db):
    from internos.activityinfo.models import Indicator

    # indicators = Indicator.objects.filter(activity__database__ai_id=ai_db.ai_id)
    indicators = Indicator.objects.filter(hpm_indicator=True)

    for indicator in indicators:
        cum_month = {}

        values = indicator.values_hpm

        for month in values:
            c_value = 0
            for c_month in range(1, int(month) + 1):
                c_value += float(values[str(c_month)])
                cum_month[str(month)] = c_value

        indicator.cumulative_values_hpm = {
            'months': cum_month,
        }
        indicator.save()

    return indicators.count()


def calculate_master_indicators_values(ai_db, report_type=None, sub_indicators=False):
    from internos.activityinfo.models import Indicator, ActivityReport, ActivityReportLive

    if sub_indicators:
        indicators = Indicator.objects.filter(activity__database__ai_id=ai_db.ai_id,
                                              master_indicator_sub=True)
    else:
        indicators = Indicator.objects.filter(activity__database__ai_id=ai_db.ai_id,
                                              master_indicator=True)

    last_month = int(datetime.datetime.now().strftime("%m"))

    if report_type == 'live':
        report = ActivityReportLive.objects.filter(database_id=ai_db.ai_id)
        last_month = last_month + 1
    else:
        report = ActivityReport.objects.filter(database_id=ai_db.ai_id)

    if ai_db.is_funded_by_unicef:
        report = report.filter(funded_by='UNICEF')

    partners = report.values('partner_id').distinct()
    governorates = report.values('location_adminlevel_governorate_code').distinct()
    governorates1 = report.values('location_adminlevel_governorate_code').distinct()
    reporting_month = str(last_month - 1)

    for indicator in indicators:
        for month in range(1, last_month):
            month = str(month)
            values_month = 0
            values_gov = {}
            values_partners = {}
            values_partners_gov = {}
            sub_indicators = indicator.summation_sub_indicators.all()
            for sub_ind in sub_indicators:
                if report_type == 'live':
                    values_month += float(sub_ind.values_live[month]) if month in sub_ind.values_live else 0
                else:
                    values_month += float(sub_ind.values[month]) if month in sub_ind.values else 0

                for gov1 in governorates1:
                    key = "{}-{}".format(month, gov1['location_adminlevel_governorate_code'])
                    if report_type == 'live':
                        value = float(sub_ind.values_gov_live[key]) if key in sub_ind.values_gov_live else 0
                    else:
                        value = float(sub_ind.values_gov[key]) if key in sub_ind.values_gov else 0
                    values_gov[key] = values_gov[key] + value if key in values_gov else value

                for partner in partners:
                    key1 = "{}-{}".format(month, partner['partner_id'])
                    if report_type == 'live':
                        value = float(sub_ind.values_partners_live[key1]) if key1 in sub_ind.values_partners_live else 0
                    else:
                        value = float(sub_ind.values_partners[key1]) if key1 in sub_ind.values_partners else 0
                    values_partners[key1] = values_partners[key1] + value if key1 in values_partners else value

                    for gov in governorates:
                        key2 = "{}-{}-{}".format(month, partner['partner_id'], gov['location_adminlevel_governorate_code'])
                        if report_type == 'live':
                            value = float(sub_ind.values_partners_gov_live[key2]) if key2 in sub_ind.values_partners_gov_live else 0
                        else:
                            value = float(sub_ind.values_partners_gov[key2]) if key2 in sub_ind.values_partners_gov else 0
                        values_partners_gov[key2] = values_partners_gov[key2] + value if key2 in values_partners_gov else value

            if report_type == 'live':
                indicator.values_live[month] = values_month
                indicator.values_gov_live.update(values_gov)
                indicator.values_partners_live.update(values_partners)
                indicator.values_partners_gov_live.update(values_partners_gov)
            else:
                if month == reporting_month:
                    indicator.values_hpm[reporting_month] = values_month
                indicator.values[month] = values_month
                indicator.values_gov.update(values_gov)
                indicator.values_partners.update(values_partners)
                indicator.values_partners_gov.update(values_partners_gov)

        indicator.save()


def calculate_indicators_values_percentage(ai_db, report_type=None):
    from internos.activityinfo.models import Indicator, ActivityReport,ActivityReportLive

    indicators = Indicator.objects.filter(activity__database__ai_id=ai_db.ai_id,
                                          calculated_indicator=True)

    last_month = int(datetime.datetime.now().strftime("%m"))

    if report_type == 'live':
        report = ActivityReportLive.objects.filter(database_id=ai_db.ai_id)
        last_month = last_month + 1
    else:
        report = ActivityReport.objects.filter(database_id=ai_db.ai_id)
    if ai_db.is_funded_by_unicef:
        report = report.filter(funded_by='UNICEF')

    partners = report.values('partner_id').distinct()
    governorates = report.values('location_adminlevel_governorate_code').distinct()
    governorates1 = report.values('location_adminlevel_governorate_code').distinct()
    reporting_month = str(last_month - 1)

    for indicator in indicators:
        for month in range(1, last_month):
            month = str(month)
            values_month = 0
            values_gov = {}
            values_partners = {}
            values_partners_gov = {}
            top_indicator = indicator.sub_indicators.all().first()
            reporting_level = top_indicator.activity.name
            percentage = indicator.calculated_percentage

            try:
                if report_type == 'live':
                    denominator = top_indicator.values_live[month] if month in top_indicator.values_live else 0
                else:
                    denominator = top_indicator.values[month] if month in top_indicator.values else 0
                if reporting_level == 'Municipality level':
                    values_month = denominator * percentage / 100
                elif reporting_level == 'Site level':
                    values_month = denominator * percentage / 100
            except Exception:
                values_month = 0

            for gov1 in governorates1:
                key = "{}-{}".format(month, gov1['location_adminlevel_governorate_code'])
                try:
                    if report_type == 'live':
                        denominator = top_indicator.values_gov_live[key] if key in top_indicator.values_gov_live else 0
                    else:
                        denominator = top_indicator.values_gov[key] if key in top_indicator.values_gov else 0
                    if reporting_level == 'Municipality level':
                        values_gov[key] = denominator * percentage / 100
                    elif reporting_level == 'Site level':
                        values_gov[key] = denominator * percentage / 100
                except Exception:
                    values_gov[key] = 0

            for partner in partners:
                key1 = "{}-{}".format(month, partner['partner_id'])

                try:
                    if report_type == 'live':
                        denominator = top_indicator.values_partners_live[key1] if key1 in top_indicator.values_partners_live else 0
                    else:
                        denominator = top_indicator.values_partners[key1] if key1 in top_indicator.values_partners else 0
                    if reporting_level == 'Municipality level':
                        values_partners[key1] = denominator * percentage / 100
                    elif reporting_level == 'Site level':
                        values_partners[key1] = denominator * percentage / 100
                except Exception:
                    values_partners[key1] = 0

                for gov in governorates:
                    key2 = "{}-{}-{}".format(month, partner['partner_id'], gov['location_adminlevel_governorate_code'])
                    try:
                        if report_type == 'live':
                            denominator = top_indicator.values_partners_gov_live[key2] if key2 in top_indicator.values_partners_gov_live else 0
                        else:
                            denominator = top_indicator.values_partners_gov[key2] if key2 in top_indicator.values_partners_gov else 0
                        if reporting_level == 'Municipality level':
                            values_partners_gov[key2] = denominator * percentage / 100
                        elif reporting_level == 'Site level':
                            values_partners_gov[key2] = denominator * percentage / 100
                    except Exception:
                        values_partners_gov[key2] = 0

            if report_type == 'live':
                indicator.values_live[month] = values_month
                indicator.values_gov_live.update(values_gov)
                indicator.values_partners_live.update(values_partners)
                indicator.values_partners_gov_live.update(values_partners_gov)
            else:
                if month == reporting_month:
                    indicator.values_hpm[reporting_month] = values_month
                indicator.values[month] = values_month
                indicator.values_gov.update(values_gov)
                indicator.values_partners.update(values_partners)
                indicator.values_partners_gov.update(values_partners_gov)

        indicator.save()


def calculate_master_indicators_values_percentage(ai_db, report_type=None):
    from internos.activityinfo.models import Indicator, ActivityReport, ActivityReportLive

    indicators = Indicator.objects.filter(activity__database__ai_id=ai_db.ai_id,
                                          master_indicator=True,
                                          measurement_type='percentage')
    last_month = int(datetime.datetime.now().strftime("%m"))

    if report_type == 'live':
        report = ActivityReportLive.objects.filter(database_id=ai_db.ai_id)
        last_month = last_month + 1
    else:
        report = ActivityReport.objects.filter(database_id=ai_db.ai_id)
    if ai_db.is_funded_by_unicef:
        report = report.filter(funded_by='UNICEF')

    partners = report.values('partner_id').distinct()
    governorates = report.values('location_adminlevel_governorate_code').distinct()
    governorates1 = report.values('location_adminlevel_governorate_code').distinct()
    reporting_month = str(last_month - 1)

    for indicator in indicators:
        for month in range(1, last_month):
            month = str(month)
            values_gov = {}
            values_partners = {}
            values_partners_gov = {}
            denominator_indicator = indicator.denominator_indicator
            numerator_indicator = indicator.numerator_indicator
            if not denominator_indicator or not numerator_indicator:
                continue
            try:
                if report_type == 'live':
                    denominator = denominator_indicator.values_live[month] if month in denominator_indicator.values_live else 0
                    numerator = numerator_indicator.values_live[month] if month in numerator_indicator.values_live else 0
                else:
                    denominator = denominator_indicator.values[month] if month in denominator_indicator.values else 0
                    numerator = numerator_indicator.values[month] if month in numerator_indicator.values else 0
                values_month = numerator / denominator
            except Exception:
                values_month = 0

            for gov1 in governorates1:
                key = "{}-{}".format(month, gov1['location_adminlevel_governorate_code'])
                try:
                    if report_type == 'live':
                        denominator = denominator_indicator.values_gov_live[key] if key in denominator_indicator.values_gov_live else 0
                        numerator = numerator_indicator.values_gov_live[key] if key in numerator_indicator.values_gov_live else 0
                    else:
                        denominator = denominator_indicator.values_gov[key] if key in denominator_indicator.values_gov else 0
                        numerator = numerator_indicator.values_gov[key] if key in numerator_indicator.values_gov else 0
                    values_gov[key] = numerator / denominator
                except Exception:
                    values_gov[key] = 0

            for partner in partners:
                key1 = "{}-{}".format(month, partner['partner_id'])

                try:
                    if report_type == 'live':
                        denominator = denominator_indicator.values_partners_live[key1] if key1 in denominator_indicator.values_partners_live else 0
                        numerator = numerator_indicator.values_partners_live[key1] if key1 in numerator_indicator.values_partners_live else 0
                    else:
                        denominator = denominator_indicator.values_partners[key1] if key1 in denominator_indicator.values_partners else 0
                        numerator = numerator_indicator.values_partners[key1] if key1 in numerator_indicator.values_partners else 0
                    values_partners[key1] = numerator / denominator
                except Exception:
                    values_partners[key1] = 0

                for gov in governorates:
                    key2 = "{}-{}-{}".format(month, partner['partner_id'], gov['location_adminlevel_governorate_code'])
                    try:
                        if report_type == 'live':
                            denominator = denominator_indicator.values_partners_gov_live[key2] if key2 in denominator_indicator.values_partners_gov_live else 0
                            numerator = numerator_indicator.values_partners_gov_live[key2] if key2 in numerator_indicator.values_partners_gov_live else 0
                        else:
                            denominator = denominator_indicator.values_partners_gov[key2] if key2 in denominator_indicator.values_partners_gov else 0
                            numerator = numerator_indicator.values_partners_gov[key2] if key2 in numerator_indicator.values_partners_gov else 0
                        values_partners_gov[key2] = numerator / denominator
                    except Exception:
                        values_partners_gov[key2] = 0

            if report_type == 'live':
                indicator.values_live[month] = values_month
                indicator.values_gov_live.update(values_gov)
                indicator.values_partners_live.update(values_partners)
                indicator.values_partners_gov_live.update(values_partners_gov)
            else:
                if month == reporting_month:
                    indicator.values_hpm[reporting_month] = values_month
                indicator.values[month] = values_month
                indicator.values_gov.update(values_gov)
                indicator.values_partners.update(values_partners)
                indicator.values_partners_gov.update(values_partners_gov)

        indicator.save()


def calculate_master_indicators_values_denominator_multiplication(ai_db, report_type=None):
    from internos.activityinfo.models import Indicator, ActivityReport, ActivityReportLive

    indicators = Indicator.objects.filter(activity__database__ai_id=ai_db.ai_id,
                                          master_indicator=True,
                                          measurement_type='percentage_x')

    last_month = int(datetime.datetime.now().strftime("%m"))

    if report_type == 'live':
        report = ActivityReportLive.objects.filter(database_id=ai_db.ai_id)
        last_month = last_month + 1
    else:
        report = ActivityReport.objects.filter(database_id=ai_db.ai_id)
    if ai_db.is_funded_by_unicef:
        report = report.filter(funded_by='UNICEF')

    partners = report.values('partner_id').distinct()
    governorates = report.values('location_adminlevel_governorate_code').distinct()
    governorates1 = report.values('location_adminlevel_governorate_code').distinct()
    reporting_month = str(last_month - 1)

    for indicator in indicators:
        for month in range(1, last_month):
            month = str(month)
            values_gov = {}
            values_partners = {}
            values_partners_gov = {}
            denominator_indicator = indicator.denominator_indicator
            numerator_indicator = indicator.numerator_indicator
            denominator_multiplication = indicator.denominator_multiplication
            if not denominator_indicator or not numerator_indicator:
                continue
            try:
                if report_type == 'live':
                    denominator = denominator_indicator.values_live[month] if month in denominator_indicator.values_live else 0
                    numerator = numerator_indicator.values_live[month] if month in numerator_indicator.values_live else 0
                else:
                    denominator = denominator_indicator.values[month] if month in denominator_indicator.values else 0
                    numerator = numerator_indicator.values[month] if month in numerator_indicator.values else 0
                denominator = denominator * denominator_multiplication
                values_month = numerator / denominator
            except Exception as ex:
                values_month = 0

            for gov1 in governorates1:
                key = "{}-{}".format(month, gov1['location_adminlevel_governorate_code'])
                try:
                    if report_type == 'live':
                        denominator = denominator_indicator.values_gov_live[key] if key in denominator_indicator.values_gov_live else 0
                        numerator = numerator_indicator.values_gov_live[key] if key in numerator_indicator.values_gov_live else 0
                    else:
                        denominator = denominator_indicator.values_gov[key] if key in denominator_indicator.values_gov else 0
                        numerator = numerator_indicator.values_gov[key] if key in numerator_indicator.values_gov else 0
                    denominator = denominator * denominator_multiplication
                    values_gov[key] = numerator / denominator
                except Exception:
                    values_gov[key] = 0

            for partner in partners:
                key1 = "{}-{}".format(month, partner['partner_id'])

                try:
                    if report_type == 'live':
                        denominator = denominator_indicator.values_partners_live[key1] if key1 in denominator_indicator.values_partners_live else 0
                        numerator = numerator_indicator.values_partners_live[key1] if key1 in numerator_indicator.values_partners_live else 0
                    else:
                        denominator = denominator_indicator.values_partners[key1] if key1 in denominator_indicator.values_partners else 0
                        numerator = numerator_indicator.values_partners[key1] if key1 in numerator_indicator.values_partners else 0
                    denominator = denominator * denominator_multiplication
                    values_partners[key1] = numerator / denominator
                except Exception:
                    values_partners[key1] = 0

                for gov in governorates:
                    key2 = "{}-{}-{}".format(month, partner['partner_id'], gov['location_adminlevel_governorate_code'])
                    try:
                        if report_type == 'live':
                            denominator = denominator_indicator.values_partners_gov_live[key2] if key2 in denominator_indicator.values_partners_gov_live else 0
                            numerator = numerator_indicator.values_partners_gov_live[key2] if key2 in numerator_indicator.values_partners_gov_live else 0
                        else:
                            denominator = denominator_indicator.values_partners_gov[key2] if key2 in denominator_indicator.values_partners_gov else 0
                            numerator = numerator_indicator.values_partners_gov[key2] if key2 in numerator_indicator.values_partners_gov else 0
                        denominator = denominator * denominator_multiplication
                        values_partners_gov[key2] = numerator / denominator
                    except Exception:
                        values_partners_gov[key2] = 0

            if report_type == 'live':
                indicator.values_live[month] = values_month
                indicator.values_gov_live.update(values_gov)
                indicator.values_partners_live.update(values_partners)
                indicator.values_partners_gov_live.update(values_partners_gov)
            else:
                if month == reporting_month:
                    indicator.values_hpm[reporting_month] = values_month
                indicator.values[month] = values_month
                indicator.values_gov.update(values_gov)
                indicator.values_partners.update(values_partners)
                indicator.values_partners_gov.update(values_partners_gov)

        indicator.save()


def calculate_individual_indicators_values(ai_db, report_type=None):
    from internos.activityinfo.models import Indicator, ActivityReport, ActivityReportLive

    last_month = int(datetime.datetime.now().strftime("%m"))

    if report_type == 'live':
        report = ActivityReportLive.objects.filter(database_id=ai_db.ai_id)
        last_month = last_month + 1
    else:
        report = ActivityReport.objects.filter(database_id=ai_db.ai_id)
    if ai_db.is_funded_by_unicef:
        report = report.filter(funded_by='UNICEF')

    indicators = Indicator.objects.filter(activity__database__ai_id=ai_db.ai_id)
    partners = report.values('partner_id').distinct()
    governorates = report.values('location_adminlevel_governorate_code').distinct()
    governorates1 = report.values('location_adminlevel_governorate_code').distinct()
    reporting_month = str(last_month - 1)

    for indicator in indicators:
        for month in range(1, last_month):
            month = str(month)
            result = get_individual_indicator_value(ai_db, indicator, month, report_type=report_type)
            if report_type == 'live':
                indicator.values_live[str(month)] = result
            else:
                if month == reporting_month:
                    indicator.values_hpm[reporting_month] = result
                indicator.values[str(month)] = result

            for gov1 in governorates1:
                key = "{}-{}".format(month, gov1['location_adminlevel_governorate_code'])
                value = get_individual_indicator_value(ai_db=ai_db, indicator_id=indicator, month=month,
                                                       gov=gov1['location_adminlevel_governorate_code'],
                                                       report_type=report_type)

                if report_type == 'live':
                    indicator.values_gov_live[str(key)] = value
                else:
                    indicator.values_gov[str(key)] = value

            for partner in partners:
                key1 = "{}-{}".format(month, partner['partner_id'])
                value1 = get_individual_indicator_value(ai_db=ai_db, indicator_id=indicator, month=month,
                                                        partner=partner['partner_id'], report_type=report_type)

                if report_type == 'live':
                    indicator.values_partners_live[str(key1)] = value1
                else:
                    indicator.values_partners[str(key1)] = value1

                for gov in governorates:
                    key2 = "{}-{}-{}".format(month, partner['partner_id'], gov['location_adminlevel_governorate_code'])
                    value2 = get_individual_indicator_value(ai_db=ai_db, indicator_id=indicator, month=month,
                                                            partner=partner['partner_id'], report_type=report_type,
                                                            gov=gov['location_adminlevel_governorate_code'])

                    if report_type == 'live':
                        indicator.values_partners_gov_live[str(key2)] = value2
                    else:
                        indicator.values_partners_gov[str(key2)] = value2

            indicator.save()

    return indicators.count()


def calculate_indicators_status(database):
    from internos.activityinfo.models import Indicator

    year_days = 365
    today = datetime.datetime.now()
    reporting_year = database.reporting_year
    beginning_year = datetime.datetime(int(reporting_year.name), 01, 01)
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
            indicator.status_color = '#FF0000'
        elif cumulative_per > over_target:
            indicator.status = 'Over Target'
            indicator.status_color = '#FFA500'
        else:
            indicator.status = 'On Track'
            indicator.status_color = '#008000'

        indicator.save()

    return indicators.count()


def get_individual_indicator_value(ai_db, indicator_id, month=None, partner=None, gov=None, report_type=None):
    from internos.activityinfo.models import ActivityReport, ActivityReportLive

    if report_type == 'live':
        reports = ActivityReportLive.objects.filter(ai_indicator=indicator_id)
    else:
        reports = ActivityReport.objects.filter(ai_indicator=indicator_id)
    if ai_db.is_funded_by_unicef:
        reports = reports.filter(funded_by='UNICEF')

    if month:
        reports = reports.filter(start_date__month=month)
        # reports = reports.filter(month=month)
    if partner:
        reports = reports.filter(partner_id=partner)
    if gov:
        reports = reports.filter(location_adminlevel_governorate_code=gov)

    total = reports.aggregate(Sum('indicator_value'))
    return total['indicator_value__sum'] if total['indicator_value__sum'] else 0


def update_partner_data(ai_db):
    from .client import ActivityInfoClient
    from .models import Partner

    client = ActivityInfoClient(ai_db.username, ai_db.password)

    dbs = client.get_databases()
    db_ids = [db['id'] for db in dbs]
    if ai_db.ai_id not in db_ids:
        raise Exception(
            'DB with ID {} not found in ActivityInfo'.format(
                ai_db.ai_id
            ))

    db_info = client.get_database(ai_db.ai_id)

    objects = 0
    try:
        if 'databasePartners' in db_info:
            partners = db_info['databasePartners']
        else:
            partners = db_info['partners']

        for partner in partners:
            try:
                ai_partner = Partner.objects.get(ai_id=partner['id'])
            except Partner.DoesNotExist:
                ai_partner = Partner(ai_id=partner['id'])
                objects += 1
            ai_partner.name = partner['name']
            ai_partner.full_name = partner['fullName']
            ai_partner.database = ai_db
            ai_partner.save()

    except Exception as e:
        raise e

    return objects


def update_hpm_table_docx(indicators, month, month_name, filename):

    from docx import Document
    from internos.activityinfo.templatetags.util_tags import get_indicator_hpm_data

    path = os.path.dirname(os.path.abspath(__file__))
    path2file = path+'/AIReports/HPM Table template 2019.docx'

    document = Document(path2file)

    document.paragraphs[0].runs[1].text = month_name

    # Education 1
    document.tables[0].rows[2].cells[6].paragraphs[0].runs[0].text = str(get_indicator_hpm_data(3942, month)['cumulative'])
    document.tables[0].rows[2].cells[7].paragraphs[0].runs[0].text = str(get_indicator_hpm_data(3942, month)['last_report_changes'])

    document.tables[0].rows[3].cells[6].paragraphs[0].runs[0].text = str(get_indicator_hpm_data(3942, month)['cumulative'])
    document.tables[0].rows[3].cells[7].paragraphs[0].runs[0].text = str(get_indicator_hpm_data(3942, month)['last_report_changes'])

    document.tables[0].rows[4].cells[6].paragraphs[0].runs[0].text = str(get_indicator_hpm_data(3942, month)['cumulative'])
    document.tables[0].rows[4].cells[7].paragraphs[0].runs[0].text = str(get_indicator_hpm_data(3942, month)['last_report_changes'])

    # Education 2
    document.tables[0].rows[5].cells[6].paragraphs[0].runs[0].text = str(get_indicator_hpm_data(3985, month)['cumulative'])
    document.tables[0].rows[5].cells[7].paragraphs[0].runs[0].text = str(get_indicator_hpm_data(3985, month)['last_report_changes'])

    document.tables[0].rows[6].cells[6].paragraphs[0].runs[0].text = str(get_indicator_hpm_data(3985, month)['cumulative'])
    document.tables[0].rows[6].cells[7].paragraphs[0].runs[0].text = str(get_indicator_hpm_data(3985, month)['last_report_changes'])

    document.tables[0].rows[7].cells[6].paragraphs[0].runs[0].text = str(get_indicator_hpm_data(3985, month)['cumulative'])
    document.tables[0].rows[7].cells[7].paragraphs[0].runs[0].text = str(get_indicator_hpm_data(3985, month)['last_report_changes'])

    document.tables[0].rows[8].cells[6].paragraphs[0].runs[0].text = str(get_indicator_hpm_data(3985, month)['cumulative'])
    document.tables[0].rows[8].cells[7].paragraphs[0].runs[0].text = str(get_indicator_hpm_data(3985, month)['last_report_changes'])

    # CP
    document.tables[0].rows[10].cells[6].paragraphs[0].runs[0].text = str(get_indicator_hpm_data(1789, month)['cumulative'])
    document.tables[0].rows[10].cells[7].paragraphs[0].runs[0].text = str(get_indicator_hpm_data(1789, month)['last_report_changes'])

    document.tables[0].rows[11].cells[6].paragraphs[0].runs[0].text = str(get_indicator_hpm_data(1654, month)['cumulative'])
    document.tables[0].rows[11].cells[7].paragraphs[0].runs[0].text = str(get_indicator_hpm_data(1654, month)['last_report_changes'])

    document.tables[0].rows[12].cells[6].paragraphs[0].runs[0].text = str(get_indicator_hpm_data(2740, month)['cumulative'])
    document.tables[0].rows[12].cells[7].paragraphs[0].runs[0].text = str(get_indicator_hpm_data(2740, month)['last_report_changes'])

    # WASH
    document.tables[0].rows[14].cells[6].paragraphs[0].runs[0].text = str(get_indicator_hpm_data(1519, month)['cumulative'])
    document.tables[0].rows[14].cells[7].paragraphs[0].runs[0].text = str(get_indicator_hpm_data(1519, month)['last_report_changes'])

    document.tables[0].rows[15].cells[6].paragraphs[0].runs[0].text = str(get_indicator_hpm_data(1527, month)['cumulative'])
    document.tables[0].rows[15].cells[7].paragraphs[0].runs[0].text = str(get_indicator_hpm_data(1527, month)['last_report_changes'])

    document.tables[0].rows[16].cells[6].paragraphs[0].runs[0].text = str(get_indicator_hpm_data(1504, month)['cumulative'])
    document.tables[0].rows[16].cells[7].paragraphs[0].runs[0].text = str(get_indicator_hpm_data(1504, month)['last_report_changes'])

    document.tables[0].rows[17].cells[6].paragraphs[0].runs[0].text = str(get_indicator_hpm_data(1535, month)['cumulative'])
    document.tables[0].rows[17].cells[7].paragraphs[0].runs[0].text = str(get_indicator_hpm_data(1535, month)['last_report_changes'])

    # H&N
    document.tables[0].rows[19].cells[6].paragraphs[0].runs[0].text = str(get_indicator_hpm_data(2621, month)['cumulative'])
    document.tables[0].rows[19].cells[7].paragraphs[0].runs[0].text = str(get_indicator_hpm_data(2621, month)['last_report_changes'])

    document.tables[0].rows[20].cells[6].paragraphs[0].runs[0].text = str(get_indicator_hpm_data(2638, month)['cumulative'])
    document.tables[0].rows[20].cells[7].paragraphs[0].runs[0].text = str(get_indicator_hpm_data(2638, month)['last_report_changes'])

    document.tables[0].rows[21].cells[6].paragraphs[0].runs[0].text = str(get_indicator_hpm_data(2178, month)['cumulative'])
    document.tables[0].rows[21].cells[7].paragraphs[0].runs[0].text = str(get_indicator_hpm_data(2178, month)['last_report_changes'])

    # Y&A
    document.tables[0].rows[23].cells[6].paragraphs[0].runs[0].text = str(get_indicator_hpm_data(3032, month)['cumulative'])
    document.tables[0].rows[23].cells[7].paragraphs[0].runs[0].text = str(get_indicator_hpm_data(3032, month)['last_report_changes'])

    document.tables[0].rows[24].cells[6].paragraphs[0].runs[0].text = str(get_indicator_hpm_data(3071, month)['cumulative'])
    document.tables[0].rows[24].cells[7].paragraphs[0].runs[0].text = str(get_indicator_hpm_data(3071, month)['last_report_changes'])

    document.tables[0].rows[25].cells[6].paragraphs[0].runs[0].text = str(get_indicator_hpm_data(3179, month)['cumulative'])
    document.tables[0].rows[25].cells[7].paragraphs[0].runs[0].text = str(get_indicator_hpm_data(3179, month)['last_report_changes'])

    document.tables[0].rows[26].cells[6].paragraphs[0].runs[0].text = str(get_indicator_hpm_data(3347, month)['cumulative'])
    document.tables[0].rows[26].cells[7].paragraphs[0].runs[0].text = str(get_indicator_hpm_data(3347, month)['last_report_changes'])

    # SP
    document.tables[0].rows[28].cells[6].paragraphs[0].runs[0].text = str(get_indicator_hpm_data(850, month)['cumulative'])
    document.tables[0].rows[28].cells[7].paragraphs[0].runs[0].text = str(get_indicator_hpm_data(850, month)['last_report_changes'])

    document.tables[0].rows[29].cells[6].paragraphs[0].runs[0].text = str(get_indicator_hpm_data(783, month)['cumulative'])
    document.tables[0].rows[29].cells[7].paragraphs[0].runs[0].text = str(get_indicator_hpm_data(783, month)['last_report_changes'])

    # C4D
    document.tables[0].rows[31].cells[6].paragraphs[0].runs[0].text = str(get_indicator_hpm_data(1396, month)['cumulative'])
    document.tables[0].rows[31].cells[7].paragraphs[0].runs[0].text = str(get_indicator_hpm_data(1396, month)['last_report_changes'])

    # PPL
    document.tables[0].rows[33].cells[6].paragraphs[0].runs[0].text = str(get_indicator_hpm_data(1121, month)['cumulative'])
    document.tables[0].rows[33].cells[7].paragraphs[0].runs[0].text = str(get_indicator_hpm_data(1121, month)['last_report_changes'])

    document.tables[0].rows[34].cells[6].paragraphs[0].runs[0].text = str(get_indicator_hpm_data(1149, month)['cumulative'])
    document.tables[0].rows[34].cells[7].paragraphs[0].runs[0].text = str(get_indicator_hpm_data(1149, month)['last_report_changes'])

    document.tables[0].rows[35].cells[6].paragraphs[0].runs[0].text = str(get_indicator_hpm_data(1178, month)['cumulative'])
    document.tables[0].rows[35].cells[7].paragraphs[0].runs[0].text = str(get_indicator_hpm_data(1178, month)['last_report_changes'])

    document.tables[0].rows[36].cells[6].paragraphs[0].runs[0].text = str(get_indicator_hpm_data(1195, month)['cumulative'])
    document.tables[0].rows[36].cells[7].paragraphs[0].runs[0].text = str(get_indicator_hpm_data(1195, month)['last_report_changes'])

    document.tables[0].rows[37].cells[6].paragraphs[0].runs[0].text = str(get_indicator_hpm_data(1293, month)['cumulative'])
    document.tables[0].rows[37].cells[7].paragraphs[0].runs[0].text = str(get_indicator_hpm_data(1293, month)['last_report_changes'])

    document.tables[0].rows[38].cells[6].paragraphs[0].runs[0].text = str(get_indicator_hpm_data(1299, month)['cumulative'])
    document.tables[0].rows[38].cells[7].paragraphs[0].runs[0].text = str(get_indicator_hpm_data(1299, month)['last_report_changes'])

    path2file2 = '{}/{}/{}'.format(path, 'AIReports', filename)
    document.save(path2file2)
    return path2file2


def update_hpm_table_docx1(indicators, month, filename):

    # import sys
    # import docx
    from docx import Document
    from internos.activityinfo.templatetags.util_tags import get_indicator_cumulative, get_indicator_hpm_data

    path = os.path.dirname(os.path.abspath(__file__))
    path2file = path+'/AIReports/HPM Table template 2019.docx'
    # path2file = path+'/AIReports/test.docx'

    document = Document(path2file)

    table = document.tables[0]

    for indicator in indicators:
        # cum_key = '#{}_cum#'.format(indicator.id)
        cum_key = str(indicator.id)
        # diff_key = '#{}_diff#'.format(indicator.id)
        diff_key = str(indicator.id)

        for row in range(0, 40):
            # try:
            p = table.rows[row].cells[6].paragraphs[0]
            # for p in table.rows[row].cells[6].paragraphs:
            if cum_key in p.text:
                inline = p.runs
                # Loop added to work with runs (strings with same style)
                for i in range(len(inline)):
                    if cum_key in inline[i].text:
                        document.tables[0].rows[row].cells[6].paragraphs[0].runs[i].text = get_indicator_cumulative(indicator, month)

            p = table.rows[row].cells[7].paragraphs[0]
            # for p in table.rows[row].cells[7].paragraphs:
            # print(diff_key)
            # if diff_key in p.text:
            #     print(p.text)

            inline = p.runs
            # print(inline)
            # Loop added to work with runs (strings with same style)
            for i in range(len(inline)):
                # if diff_key == '1504':
                # print(inline[i].text)
                if diff_key in inline[i].text:
                    document.tables[0].rows[row].cells[7].paragraphs[0].runs[i].text = get_indicator_diff_results(indicator, month)

            # except Exception as ex:
                # print(ex.message)
                # continue

    path2file2 = '{}/{}/{}'.format(path, 'AIReports', filename)
    document.save(path2file2)
    return path2file2
