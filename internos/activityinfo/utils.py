import os
import csv
import json
import datetime
import subprocess
from django.db.models import Sum
from django.conf import settings


def r_script_command_line(script_name, ai_db):
    command = 'Rscript'
    path = os.path.dirname(os.path.abspath(__file__))
    path2script = path+'/RScripts/'+script_name

    cmd = [command, path2script, ai_db.username, ai_db.password, str(ai_db.ai_id)]

    try:
        subprocess.check_output(cmd, universal_newlines=True)
    except subprocess.CalledProcessError as e:
        print("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
        return 0

    return 1


def read_data_from_file(ai_id):
    from internos.activityinfo.models import Database
    from internos.backends.models import ImportLog
    month_name = datetime.datetime.now().strftime("%B")

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


def add_rows(ai_id):
    from internos.activityinfo.models import ActivityReport

    month = datetime.datetime.now().strftime("%M")
    month_name = datetime.datetime.now().strftime("%B")
    path = os.path.dirname(os.path.abspath(__file__))
    path2file = path+'/AIReports/'+str(ai_id)+'_ai_data.csv'
    ctr = 0

    with open(path2file) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            ctr += 1
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
                indicator_value=row['indicator.value'] if 'indicator.value' in row else '',
                funded_by=row['Funded_by'] if 'Funded_by' in row else '',
                location_latitude=row['location.latitude'] if 'location.latitude' in row else '',
                indicator_category=row['indicator.category'] if 'indicator.category' in row else '',
                location_alternate_name=row[
                    'location.alternate_name'] if 'location.alternate_name' in row else '',
                start_date=row['start_date'] if 'start_date' in row and not row['start_date'] == 'NA' else None,
                location_adminlevel_cadastral_area=unicode(row['location.adminlevel.cadastral_area'],
                                                              errors='replace') if 'location.adminlevel.cadastral_area' in row else '',
                location_adminlevel_governorate=row[
                    'location.adminlevel.governorate'] if 'location.adminlevel.governorate' in row else '',
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


def link_indicators_data(ai_id):
    from internos.activityinfo.models import Indicator, ActivityReport

    ctr = 0
    reports = ActivityReport.objects.filter(database_id=ai_id, funded_by='UNICEF')
    indicators = Indicator.objects.filter(activity__database__ai_id=ai_id)

    for item in indicators:
        ai_values = reports.filter(indicator_id=item.ai_indicator)
        if not ai_values.count():
            continue
        ctr += 1
        item.update(funded_by='UNICEF')
        ai_values.update(ai_indicator=item)

    return ctr


def calculate_indicators_values(ai_id):
    from internos.activityinfo.models import Indicator, ActivityReport

    report = ActivityReport.objects.filter(database_id=ai_id)
    indicators = Indicator.objects.filter(activity__database__ai_id=ai_id)
    # indicators = Indicator.objects.filter(activity__database__ai_id=ai_id, master_indicator=True)
    partners = report.values('partner_id').distinct()
    governorates = report.values('location_adminlevel_governorate_code').distinct()
    governorates1 = report.values('location_adminlevel_governorate_code').distinct()

    partners_list = {}
    governorates_list = {}

    for indicator in indicators:
        months = {}
        values_gov = {}
        values_partners = {}
        values_partners_gov = {}
        cumulative_results = 0
        level = 1 if indicator.master_indicator_sub else 0
        level = 2 if indicator.master_indicator else level

        for month in range(0, 13):
            result = get_indicator_value(indicator, level, month)
            cumulative_results += result
            months[str(month)] = result

            for gov1 in governorates1:
                key = "{}-{}".format(month, gov1['location_adminlevel_governorate_code'])
                value = get_indicator_value(indicator_id=indicator,
                                            level=level, month=month,
                                            gov=gov1['location_adminlevel_governorate_code'])

                values_gov[str(key)] = value
                governorates_list[gov1['location_adminlevel_governorate_code']] = value

            for partner in partners:
                key = "{}-{}".format(month, partner['partner_id'])
                values_partners[str(key)] = get_indicator_value(indicator_id=indicator,
                                                                level=level, month=month,
                                                                partner=partner['partner_id'])

                for gov in governorates:
                    key = "{}-{}-{}".format(month, partner['partner_id'], gov['location_adminlevel_governorate_code'])
                    values_partners_gov[str(key)] = get_indicator_value(indicator_id=indicator, level=level,
                                                                        month=month, partner=partner['partner_id'],
                                                                        gov=gov['location_adminlevel_governorate_code'])

        indicator.values = months
        indicator.values_gov = values_gov
        indicator.values_partners = values_partners
        indicator.values_partners_gov = values_partners_gov
        indicator.cumulative_results = cumulative_results
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


def get_indicator_value(indicator_id, level=0, month=None, partner=None, gov=None):
    from internos.activityinfo.models import ActivityReport, Indicator

    if indicator_id.measurement_type == 'percentage':
        return get_indicator_value_percentage(indicator_id, month, partner, gov)

    reports = ActivityReport.objects.filter(funded_by='UNICEF')

    if level == 0:
        reports = reports.filter(ai_indicator=indicator_id)
    if level == 1:
        indicators = indicator_id.sub_indicators.values_list('id', flat=True).distinct()
        reports = reports.filter(ai_indicator_id__in=indicators)
    if level == 2:
        indicators = indicator_id.sub_indicators.values_list('id', flat=True).distinct()
        indicators2 = Indicator.objects.filter(
            sub_indicators__id__in=indicators
        ).exclude(master_indicator=True).values_list('id', flat=True).distinct()
        reports = reports.filter(ai_indicator_id__in=indicators2)
    if month:
        reports = reports.filter(start_date__month=month)
    if partner:
        reports = reports.filter(partner_id=partner)
    if gov:
        reports = reports.filter(location_adminlevel_governorate_code=gov)

    total = reports.aggregate(Sum('indicator_value'))
    return total['indicator_value__sum'] if total['indicator_value__sum'] else 0


def get_indicator_value_percentage(indicator_id, month=None, partner=None, gov=None):
    from internos.activityinfo.models import ActivityReport, Indicator

    reports = ActivityReport.objects.filter(funded_by='UNICEF')
    reports1 = ActivityReport.objects.filter(funded_by='UNICEF')

    denominator_summation = indicator_id.denominator_summation.values_list('id', flat=True).distinct()
    denominator_indicators = Indicator.objects.filter(
        denominator_summation__id__in=denominator_summation
    ).exclude(master_indicator=True).values_list('id', flat=True).distinct()
    reports = reports.filter(ai_indicator_id__in=denominator_indicators)

    numerator_summation = indicator_id.numerator_summation.values_list('id', flat=True).distinct()
    numerator_indicators = Indicator.objects.filter(
        numerator_summation__id__in=numerator_summation
    ).exclude(master_indicator=True).values_list('id', flat=True).distinct()
    reports1 = reports1.filter(ai_indicator_id__in=numerator_indicators)

    if month:
        reports = reports.filter(start_date__month=month)
        reports1 = reports1.filter(start_date__month=month)
    if partner:
        reports = reports.filter(partner_id=partner)
        reports1 = reports1.filter(partner_id=partner)
    if gov:
        reports = reports.filter(location_adminlevel_governorate_code=gov)
        reports1 = reports1.filter(location_adminlevel_governorate_code=gov)

    total = reports.aggregate(Sum('indicator_value'))
    total1 = reports1.aggregate(Sum('indicator_value'))
    denominator = total['indicator_value__sum'] if total['indicator_value__sum'] else 0
    numerator = total1['indicator_value__sum'] if total1['indicator_value__sum'] else 0
    try:
        return denominator / numerator
    except Exception:
        return 0


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
