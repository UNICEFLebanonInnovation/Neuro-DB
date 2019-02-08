import os
import csv
import json
import datetime
import subprocess
from django.db.models import Sum
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


def read_data_from_file(ai_id, forced=False):
    from internos.activityinfo.models import Database, ActivityReport
    from internos.backends.models import ImportLog
    month_name = datetime.datetime.now().strftime("%B")
    month = int(datetime.datetime.now().strftime("%m")) - 1

    if forced:
        ActivityReport.objects.filter(start_date__month=month).delete()
        return add_rows(ai_id, month)

    try:
        ImportLog.objects.get(
            object_id=ai_id,
            object_type='AI',
            month=month_name,
            status=True)
        return update_rows(ai_id)
    except ImportLog.DoesNotExist:
        ImportLog.objects.create(
            object_id=ai_id,
            object_name=Database.objects.get(ai_id=ai_id).name,
            object_type='AI',
            month=month_name,
            status=True)
        return add_rows(ai_id)


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


def add_rows(ai_id, selected_month=None):
    from internos.activityinfo.models import ActivityReport

    month = int(datetime.datetime.now().strftime("%m"))
    month_name = datetime.datetime.now().strftime("%B")
    path = os.path.dirname(os.path.abspath(__file__))
    path2file = path+'/AIReports/'+str(ai_id)+'_ai_data.csv'
    ctr = 0

    with open(path2file) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            ctr += 1
            # if selected_month and
            indicator_value = 0
            if 'indicator.value' in row:
                indicator_value = row['indicator.value']

            try:
                indicator_value = float(indicator_value)
            except Exception:
                indicator_value = 0

            ActivityReport.objects.create(
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
                partner_label=row['partner.label'] if 'partner.label' in row else '',
                location_adminlevel_caza_code=row[
                    'location.adminlevel.caza.code'] if 'location.adminlevel.caza.code' in row else '',
                location_adminlevel_caza=unicode(row['location.adminlevel.caza'],
                                                  errors='replace') if 'location.adminlevel.caza' in row else '',
                partner_description=unicode(row['partner.description'],
                                               errors='replace') if 'partner.description' in row else '',
                form=row['form'] if 'form' in row else '',
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
                    'location.adminlevel.governorate']) if 'location.adminlevel.governorate' in row else '',
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


def link_indicators_data(ai_db):
    from internos.activityinfo.models import Indicator, ActivityReport

    ctr = 0
    reports = ActivityReport.objects.filter(database_id=ai_db.ai_id)
    if ai_db.is_funded_by_unicef:
        reports = reports.filter(funded_by='UNICEF')
    indicators = Indicator.objects.filter(activity__database__ai_id=ai_db.ai_id).exclude(master_indicator=True).exclude(master_indicator_sub=True)

    for item in indicators:
        ai_values = reports.filter(indicator_id=item.ai_indicator)
        if not ai_values.count():
            continue
        ctr += ai_values.count()
        # if ai_db.is_funded_by_unicef:
        #     item.update(funded_by='UNICEF')
        ai_values.update(ai_indicator=item)

    return ctr


def reset_indicators_values(ai_id):
    from internos.activityinfo.models import Indicator

    indicators = Indicator.objects.filter(activity__database__ai_id=ai_id)
    for indicator in indicators:
        indicator.values = {}
        indicator.values_gov = {}
        indicator.values_partners = {}
        indicator.values_partners_gov = {}
        indicator.save()

    return indicators.count()


def calculate_indicators_values(ai_db):
    calculate_individual_indicators_values(ai_db)
    calculate_master_indicators_values(ai_db, True)
    calculate_master_indicators_values(ai_db)
    calculated_master_indicators_values_percentage(ai_db)
    calculate_indicators_cumulative_results(ai_db)

    return 0


def calculate_indicators_cumulative_results(ai_db):
    from internos.activityinfo.models import Indicator

    indicators = Indicator.objects.filter(activity__database__ai_id=ai_db.ai_id)

    for indicator in indicators:
        value = 0
        values = indicator.values
        for month in values:
            value += int(values[month])
        indicator.cumulative_results = value
        indicator.save()


def calculate_master_indicators_values(ai_db, sub_indicators=False):
    from internos.activityinfo.models import Indicator, ActivityReport

    if sub_indicators:
        indicators = Indicator.objects.filter(activity__database__ai_id=ai_db.ai_id, master_indicator_sub=True)
    else:
        indicators = Indicator.objects.filter(activity__database__ai_id=ai_db.ai_id,
                                              master_indicator=True)

    report = ActivityReport.objects.filter(database_id=ai_db.ai_id)

    if ai_db.is_funded_by_unicef:
        report = report.filter(funded_by='UNICEF')

    partners = report.values('partner_id').distinct()
    governorates = report.values('location_adminlevel_governorate_code').distinct()
    governorates1 = report.values('location_adminlevel_governorate_code').distinct()
    month = str(int(datetime.datetime.now().strftime("%m")) - 1)

    for indicator in indicators:
        values_month = 0
        values_gov = {}
        values_partners = {}
        values_partners_gov = {}
        sub_indicators = indicator.summation_sub_indicators.all()
        for sub_ind in sub_indicators:
            values_month += int(sub_ind.values[month]) if month in sub_ind.values else 0

            for gov1 in governorates1:
                key = "{}-{}".format(month, gov1['location_adminlevel_governorate_code'])
                value = int(sub_ind.values_gov[key]) if key in sub_ind.values_gov else 0
                values_gov[key] = values_gov[key] + value if key in values_gov else value

            for partner in partners:
                key1 = "{}-{}".format(month, partner['partner_id'])
                value = int(sub_ind.values_partners[key1]) if key1 in sub_ind.values_partners else 0
                values_partners[key1] = values_partners[key1] + value if key1 in values_partners else value

                for gov in governorates:
                    key2 = "{}-{}-{}".format(month, partner['partner_id'], gov['location_adminlevel_governorate_code'])
                    value = int(sub_ind.values_partners_gov[key2]) if key2 in sub_ind.values_partners_gov else 0
                    values_partners_gov[key2] = values_partners_gov[key2] + value if key2 in values_partners_gov else value

        indicator.values[month] = values_month
        indicator.values_gov.update(values_gov)
        indicator.values_partners.update(values_partners)
        indicator.values_partners_gov.update(values_partners_gov)
        indicator.save()


def calculated_master_indicators_values_percentage(ai_db):
    from internos.activityinfo.models import Indicator, ActivityReport

    indicators = Indicator.objects.filter(activity__database__ai_id=ai_db.ai_id,
                                          master_indicator=True,
                                          measurement_type='percentage')

    report = ActivityReport.objects.filter(database_id=ai_db.ai_id)
    if ai_db.is_funded_by_unicef:
        report = report.filter(funded_by='UNICEF')

    partners = report.values('partner_id').distinct()
    governorates = report.values('location_adminlevel_governorate_code').distinct()
    governorates1 = report.values('location_adminlevel_governorate_code').distinct()
    month = str(int(datetime.datetime.now().strftime("%m")) - 1)

    for indicator in indicators:
        values_gov = {}
        values_partners = {}
        values_partners_gov = {}
        denominator_indicator = indicator.denominator_indicator
        numerator_indicator = indicator.numerator_indicator
        if not denominator_indicator or not numerator_indicator:
            continue
        try:
            denominator = denominator_indicator.values[month] if month in denominator_indicator.values else 0
            numerator = numerator_indicator.values[month] if month in numerator_indicator.values else 0
            values_month = numerator / denominator
        except Exception:
            values_month = 0

        for gov1 in governorates1:
            key = "{}-{}".format(month, gov1['location_adminlevel_governorate_code'])
            try:
                denominator = denominator_indicator.values_gov[key] if key in denominator_indicator.values_gov else 0
                numerator = numerator_indicator.values_gov[key] if key in numerator_indicator.values_gov else 0
                values_gov[key] = numerator / denominator
            except Exception:
                values_gov[key] = 0

        for partner in partners:
            key1 = "{}-{}".format(month, partner['partner_id'])

            try:
                denominator = denominator_indicator.values_partners[key1] if key1 in denominator_indicator.values_partners else 0
                numerator = numerator_indicator.values_partners[key1] if key1 in numerator_indicator.values_partners else 0
                values_partners[key1] = numerator / denominator
            except Exception:
                values_partners[key1] = 0

            for gov in governorates:
                key2 = "{}-{}-{}".format(month, partner['partner_id'], gov['location_adminlevel_governorate_code'])
                try:
                    denominator = denominator_indicator.values_partners_gov[key2] if key2 in denominator_indicator.values_partners_gov else 0
                    numerator = numerator_indicator.values_partners_gov[key2] if key2 in numerator_indicator.values_partners_gov else 0
                    values_partners_gov[key2] = numerator / denominator
                except Exception:
                    values_partners_gov[key2] = 0

        indicator.values[month] = values_month
        indicator.values_gov.update(values_gov)
        indicator.values_partners.update(values_partners)
        indicator.values_partners_gov.update(values_partners_gov)
        indicator.save()


def calculate_individual_indicators_values(ai_db):
    from internos.activityinfo.models import Indicator, ActivityReport

    report = ActivityReport.objects.filter(database_id=ai_db.ai_id)
    if ai_db.is_funded_by_unicef:
        report = report.filter(funded_by='UNICEF')

    indicators = Indicator.objects.filter(activity__database__ai_id=ai_db.ai_id)
    partners = report.values('partner_id').distinct()
    governorates = report.values('location_adminlevel_governorate_code').distinct()
    governorates1 = report.values('location_adminlevel_governorate_code').distinct()
    month = int(datetime.datetime.now().strftime("%m")) - 1

    for indicator in indicators:
        result = get_individual_indicator_value(ai_db, indicator, month)
        indicator.values[str(month)] = result

        for gov1 in governorates1:
            key = "{}-{}".format(month, gov1['location_adminlevel_governorate_code'])
            value = get_individual_indicator_value(ai_db=ai_db, indicator_id=indicator, month=month,
                                                   gov=gov1['location_adminlevel_governorate_code'])

            indicator.values_gov[str(key)] = value

        for partner in partners:
            key1 = "{}-{}".format(month, partner['partner_id'])
            value1 = get_individual_indicator_value(ai_db=ai_db, indicator_id=indicator, month=month,
                                                    partner=partner['partner_id'])

            indicator.values_partners[str(key1)] = value1

            for gov in governorates:
                key2 = "{}-{}-{}".format(month, partner['partner_id'], gov['location_adminlevel_governorate_code'])
                value2 = get_individual_indicator_value(ai_db=ai_db, indicator_id=indicator, month=month,
                                                        partner=partner['partner_id'],
                                                        gov=gov['location_adminlevel_governorate_code'])

                indicator.values_partners_gov[str(key2)] = value2

        indicator.save()

    return indicators.count()


def calculate_indicators_status(database):
    from internos.activityinfo.models import Indicator

    year_days = 365
    today = datetime.datetime.now()
    beginning_year = datetime.datetime(int(database.year if database.year else 2018), 01, 01)
    delta = today - beginning_year
    total_days = delta.days + 1
    days_passed_per = (total_days * 100) / year_days

    indicators = Indicator.objects.filter(activity__database__ai_id=database.ai_id, funded_by='UNICEF')
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


def get_individual_indicator_value(ai_db, indicator_id, month=None, partner=None, gov=None):
    from internos.activityinfo.models import ActivityReport, Indicator

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


#  not used for now
def copy_disaggregated_data(ai_id):
    from internos.activityinfo.models import Indicator, ActivityReport

    order = 0
    month = int(datetime.datetime.now().strftime("%m")) - 1
    report = ActivityReport.objects.filter(
        database_id=ai_id,
        start_date__month=month,
        funded_by__contains='UNICEF')

    top_indicators = Indicator.objects.filter(activity__database__ai_id=ai_id, master_indicator=True)
    for item in top_indicators:
        order += 1
        try:
            if item.ai_id:
                instance = report.get(indicator_id=item.ai_id)
            else:
                instance = report.get(indicator_name=item.name)
        except ActivityReport.DoesNotExist:
            instance = ActivityReport.objects.create(
                indicator_id=item.ai_id,
                indicator_name=item.name,
                database_id=ai_id,
                funded_by='UNICEF',
                start_date='2018-11-01'
            )
        instance.target = item.target
        instance.master_indicator = True
        instance.order = order
        instance.save()

        for item1 in item.sub_indicators.all():
            order += 1
            try:
                if item1.ai_id:
                    instance1 = report.get(indicator_id=item1.ai_id)
                else:
                    instance1 = report.get(indicator_name=item1.name)
            except ActivityReport.DoesNotExist:
                instance1 = ActivityReport.objects.create(
                    indicator_id=item1.ai_id,
                    indicator_name=item1.name,
                    indicator_awp_code=item1.awp_code,
                    database_id=instance.database_id,
                    funded_by=instance.funded_by,
                    start_date=instance.start_date,
                )
            instance1.master_indicator_sub = True
            instance1.target = item1.target
            instance1.order = order
            instance1.save()

            for item2 in item1.sub_indicators.exclude(master_indicator=True):
                order += 1
                if item2.ai_id:
                    instance2 = report.get(indicator_id=item2.ai_id)
                else:
                    instance2 = report.get(indicator_name=item2.name)
                instance2.target = item2.target
                instance2.order = order
                instance2.save()

    return report.count()
