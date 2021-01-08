
import json
import logging
from datetime import datetime

from internos.taskapp.celery import app
from .client import ActivityInfoClient
from .utils import r_script_command_line

logger = logging.getLogger(__name__)


def read_form_data(formid):
    client = ActivityInfoClient()
    response = client.make_request('resources/form/M2142704628/query/rows').json()
    print(response)


@app.task
def exec_import_script():
    from .models import Database

    databases = Database.objects.all()
    for db in databases:
        r_script_command_line('ai_generate_excel.R', db.ai_id)


def read_imported_data():
    from .models import Database

    databases = Database.objects.all()
    for db in databases:
        pass


@app.task
def migrate_tag(tag_name, from_tag, to_tag):
    from internos.activityinfo.models import Indicator

    indicators = Indicator.objects.filter(tag_nationality_id=int(from_tag))
    print(indicators.count())

    for indicator in indicators.iterator():
        setattr(indicator, tag_name, int(to_tag))
        indicator.save()


@app.task
def link_partners(report_type=None):
    from .utils import link_ai_partners, link_etools_partners
    link_ai_partners(report_type=report_type)
    link_etools_partners()


@app.task
def link_partners(report_type=None):
    from .utils import link_ai_locations
    link_ai_locations(report_type=report_type)


@app.task
def generate_indicators_number():
    from internos.activityinfo.models import Indicator

    for indicator in Indicator.objects.all():
        indicator.ai_indicator = indicator.get_ai_indicator
        indicator.save()


@app.task
def import_activity_data():
    from internos.activityinfo.models import Database
    from .utils import import_data_via_r_script

    databases = Database.objects.filter(reporting_year__current=True)
    for db in databases:
        logger.info('1. Import report: '+db.name)
        import_data_via_r_script(db)


@app.task
def import_data_and_generate_monthly_report(database):
    from internos.activityinfo.models import Database
    from .utils import import_data_via_r_script, link_indicators_data, calculate_indicators_values, calculate_indicators_tags

    databases = Database.objects.filter(reporting_year__current=True)
    if database:
        databases = Database.objects.filter(ai_id=database)

    for db in databases:
        print(db.name)
        logger.info('1. Import report: '+db.name)
        import_data_via_r_script(db)
        logger.info('2. Link data: ' + db.name)
        link_indicators_data(db)
        logger.info('3. Calculate indicator values')
        calculate_indicators_values(db)
        calculate_indicators_tags(db)


@app.task
def import_data_and_generate_monthly_report_sector():
    from internos.activityinfo.models import Database
    from .utils import import_data_via_r_script, link_indicators_data
    from .utils_sector import calculate_indicators_values, calculate_indicators_tags

    databases = Database.objects.filter(reporting_year__current=True, is_sector=True)
    for db in databases:
        logger.info('1. Import report: '+db.name)
        import_data_via_r_script(db)
        logger.info('2. Link data: ' + db.name)
        link_indicators_data(db)
        logger.info('3. Calculate indicator values')
        calculate_indicators_values(db)
    calculate_indicators_tags()


@app.task
def import_data_and_generate_live_report(database):
    from internos.activityinfo.models import Database
    from .utils import import_data_via_r_script, link_indicators_data, calculate_indicators_values

    databases = Database.objects.filter(reporting_year__year=datetime.now().year)
    if database:
        databases = Database.objects.filter(ai_id=database)

    for db in databases:
        print(db.name)
        print('1. Import report: '+db.name)
        import_data_via_r_script(db, report_type='live')
        print('2. Link data: ' + db.name)
        link_indicators_data(db, report_type='live')
        print('3. Calculate indicator values')
        calculate_indicators_values(db, report_type='live')


@app.task
def import_data_and_generate_live_crisis_report(database):
    from internos.activityinfo.models import Database
    from .utils_shift import import_data_via_r_script, link_indicators_data, calculate_indicators_values

    databases = Database.objects.filter(reporting_year__year=datetime.now().year)
    if database:
        databases = Database.objects.filter(ai_id=database)

    for db in databases:
        print(db.name)
        print('1. Import report: '+db.name)
        import_data_via_r_script(db, report_type='live')
        print('2. Link data: ' + db.name)
        link_indicators_data(db, report_type='live')
        print('3. Calculate indicator values')
        calculate_indicators_values(db, report_type='live')


@app.task
def import_data_and_generate_weekly_report(database):
    from internos.activityinfo.models import Database
    from .utils_shift import import_data_via_r_script, link_indicators_data, calculate_indicators_values

    databases = Database.objects.filter(reporting_year__year=datetime.now().year)
    if database:
        databases = Database.objects.filter(ai_id=database)

    for db in databases:
        print(db.name)
        print('1. Import report: '+db.name)
        import_data_via_r_script(db, report_type='weekly')
        print('2. Link data: ' + db.name)
        link_indicators_data(db, report_type='weekly')
        print('3. Calculate indicator values')
        calculate_indicators_values(db, report_type='weekly')


@app.task
def copy_indicators_values_to_hpm():
    from internos.activityinfo.models import Indicator

    indicators = Indicator.objects.all()

    for indicator in indicators:
        indicator.values_hpm = indicator.values
        indicator.save()


@app.task
def change_indicators_code():
    from internos.activityinfo.models import Indicator

    indicators = Indicator.objects.filter(activity_id=112).only('ai_indicator', 'name')
    print(indicators.count())
    indicators2 = Indicator.objects.filter(activity_id=113)
    print(indicators2.count())

    ctr = 0
    for item in indicators.iterator():
        result = Indicator.objects.filter(name=item.name, activity_id=113).exclude(ai_indicator=item.ai_indicator)
        if result.count():
            ctr += 1
            result.update(explication='PART2')
            result.update(ai_indicator=item.ai_indicator)

    print(ctr)


def import_activityinfo_locations_data():
    from internos.activityinfo.client import ActivityInfoClient
    from internos.activityinfo.models import (
        Database,
        Activity,
        AdminLevels,
        AdminLevelEntities,
        LocationTypes,
        Locations,
        Sites
    )

    ai_db = Database.objects.get(id=14)
    databases = Database.objects.all()

    client = ActivityInfoClient(ai_db.username, ai_db.password)
    country = 370

    for database in databases.iterator():
        result = client.get_sites(database=database.ai_id)
        for item in result:
            instance, create = Sites.objects.get_or_create(id=int(item['id']))
            # instance.partner_id = item['partner']['id'] if 'partner' in item else ''
            instance.partner_name = item['partner']['name'] if 'partner' in item else ''

            # instance.location_id = item['location']['id'] if 'location' in item else ''
            instance.code = item['location']['code'] if 'location' in item else ''
            instance.name = item['location']['name'] if 'location' in item else ''
            instance.latitude = item['location']['latitude'] if 'location' in item and 'latitude' in item['location'] else ''
            instance.longitude = item['location']['longitude'] if 'location' in item and 'longitude' in item['location'] else ''

            # instance.activity = Activity.objects.get(ai_id=item['activity']) if 'activity' in item else ''
            instance.database_id = database.id

            instance.save()

    result = client.get_admin_levels(country)
    for item in result:
        instance, create = AdminLevels.objects.get_or_create(id=int(item['id']))
        instance.name = item['name']
        instance.save()

        result1 = client.get_entities(item['id'])
        for item1 in result1:
            instance1, create = AdminLevelEntities.objects.get_or_create(id=int(item1['id']))
            instance1.code = item1['code']
            instance1.name = item1['name']
            instance1.parent_id = item1['parentId']
            instance1.level = instance
            instance1.bounds = item1['bounds']
            instance1.save()

    result = client.get_location_types(country)
    for item in result:
        instance, create = LocationTypes.objects.get_or_create(id=int(item['id']))
        instance.name = item['name']
        instance.save()

        result1 = client.get_locations(item['id'])
        for item1 in result1:
            instance1, create = Locations.objects.get_or_create(id=int(item1['id']))

            instance1.code = item1['code'] if 'code' in item1 else ''
            instance1.name = item1['name']
            instance1.type = instance
            instance1.longitude = item1['longitude'] if 'longitude' in item1 else ''
            instance1.latitude = item1['latitude'] if 'latitude' in item1 else ''

            instance1.save()


@app.task
def replicate_ai_indicators(db_source, db_destination):
    from internos.activityinfo.models import Database, Activity, Indicator

    activities = Activity.objects.filter(database_id=db_source)
    for activity in activities:
        indicators = activity.activity_indicators
        new_activity, created = Activity.objects.get_or_create(
            ai_id=activity.ai_id,
            ai_form_id=activity.ai_form_id,
            name=activity.name,
            database_id=db_destination,
            category=activity.category
        )

        for indicator in indicators.all():
            new_indicator, created = Indicator.objects.get_or_create(
                ai_id=indicator.ai_id,
                ai_indicator=indicator.ai_indicator,
                activity_id=new_activity.id,
                name=indicator.name
            )

            new_indicator.awp_code = indicator.awp_code
            # new_indicator.name = indicator.name
            new_indicator.label = indicator.label
            new_indicator.hpm_label = indicator.hpm_label
            new_indicator.description = indicator.description
            new_indicator.explication = indicator.explication
            new_indicator.list_header = indicator.list_header
            new_indicator.type = indicator.type
            new_indicator.reporting_level = indicator.reporting_level
            new_indicator.target = indicator.target
            new_indicator.target_sector = indicator.target_sector
            new_indicator.target_sub_total = indicator.target_sub_total
            new_indicator.units = indicator.units
            new_indicator.category = indicator.category
            new_indicator.none_ai_indicator = indicator.none_ai_indicator
            new_indicator.funded_by = indicator.funded_by
            new_indicator.sequence = indicator.sequence
            new_indicator.is_sector = indicator.is_sector
            new_indicator.is_section = indicator.is_section
            new_indicator.support_disability = indicator.support_disability
            new_indicator.support_COVID = indicator.support_COVID
            new_indicator.is_cumulative = indicator.is_cumulative
            new_indicator.is_imported = indicator.is_imported
            new_indicator.is_imported_by_calculation = indicator.is_imported_by_calculation
            new_indicator.targets = indicator.targets

            new_indicator.tag_age = indicator.tag_age
            new_indicator.tag_gender = indicator.tag_gender
            new_indicator.tag_nationality = indicator.tag_nationality
            new_indicator.tag_disability = indicator.tag_disability
            new_indicator.tag_programme = indicator.tag_programme
            new_indicator.tag_focus = indicator.tag_focus
            new_indicator.hpm_indicator = indicator.hpm_indicator
            new_indicator.comment = indicator.comment
            new_indicator.target_hpm = indicator.target_hpm
            new_indicator.has_hpm_note = indicator.has_hpm_note
            new_indicator.hpm_additional_cumulative = indicator.hpm_additional_cumulative
            new_indicator.hpm_global_indicator = indicator.hpm_global_indicator
            new_indicator.project_code = indicator.project_code
            new_indicator.project_name = indicator.project_name
            new_indicator.project = indicator.project

            new_indicator.master_indicator = indicator.master_indicator
            new_indicator.master_indicator_sub = indicator.master_indicator_sub
            new_indicator.master_indicator_sub_sub = indicator.master_indicator_sub_sub
            new_indicator.individual_indicator = indicator.individual_indicator
            new_indicator.separator_indicator = indicator.separator_indicator
            new_indicator.calculated_indicator = indicator.calculated_indicator
            new_indicator.calculated_percentage = indicator.calculated_percentage
            new_indicator.measurement_type = indicator.measurement_type
            new_indicator.denominator_multiplication = indicator.denominator_multiplication

            new_indicator.save()

        for indicator in indicators.all():
            new_indicator = Indicator.objects.get(
                ai_id=indicator.ai_id,
                ai_indicator=indicator.ai_indicator,
                activity_id=new_activity.id,
                name=indicator.name
            )

            if indicator.main_master_indicator:
                new_indicator_activity = get_new_indicator_activity(indicator.main_master_indicator.activity,
                                                                    db_destination)
                new_indicator.main_master_indicator = get_new_indicator(indicator.main_master_indicator, new_indicator_activity)
                    # Indicator.objects.get(
                    # ai_id=indicator.main_master_indicator.ai_id,
                    # ai_indicator=indicator.main_master_indicator.ai_indicator,
                    # activity__database_id=new_activity.database_id,
                    # name=indicator.main_master_indicator.name
                # )

            if indicator.numerator_indicator:
                new_indicator_activity = get_new_indicator_activity(indicator.numerator_indicator.activity,
                                                                    db_destination)
                new_indicator.numerator_indicator = get_new_indicator(indicator.numerator_indicator, new_indicator_activity)

                # new_indicator.numerator_indicator = Indicator.objects.get(
                #     ai_id=indicator.numerator_indicator.ai_id,
                #     ai_indicator=indicator.numerator_indicator.ai_indicator,
                #     activity__database_id=new_activity.database_id,
                #     name=indicator.numerator_indicator.name
                # )

            if indicator.denominator_indicator:
                new_indicator_activity = get_new_indicator_activity(indicator.denominator_indicator.activity,
                                                                    db_destination)
                new_indicator.denominator_indicator = get_new_indicator(indicator.denominator_indicator, new_indicator_activity)

                # new_indicator.denominator_indicator = Indicator.objects.get(
                #     ai_id=indicator.denominator_indicator.ai_id,
                #     ai_indicator=indicator.denominator_indicator.ai_indicator,
                #     activity__database_id=new_activity.database_id,
                #     name=indicator.denominator_indicator.name
                # )

            if indicator.sub_indicators:
                sub_indicators = indicator.sub_indicators.all()
                for sub_indicator in sub_indicators:
                    try:
                        new_indicator_activity = get_new_indicator_activity(sub_indicator.activity,
                                                                            db_destination)
                        new_sub_indicator = get_new_indicator(sub_indicator, new_indicator_activity)

                        # new_sub_indicator = Indicator.objects.get(
                        #     ai_id=sub_indicator.ai_id,
                        #     ai_indicator=sub_indicator.ai_indicator,
                        #     activity__database_id=new_activity.database_id,
                        #     name=sub_indicator.name,
                        # )
                        new_indicator.sub_indicators.add(new_sub_indicator)
                    except:
                        print(sub_indicator.name)
                        continue

            if indicator.summation_sub_indicators:
                sub_indicators = indicator.summation_sub_indicators.all()
                for sub_indicator in sub_indicators:
                    try:
                        new_indicator_activity = get_new_indicator_activity(sub_indicator.activity,
                                                                            db_destination)
                        new_sub_indicator = get_new_indicator(sub_indicator, new_indicator_activity)

                        # new_sub_indicator = Indicator.objects.get(
                        #     ai_id=sub_indicator.ai_id,
                        #     ai_indicator=sub_indicator.ai_indicator,
                        #     activity__database_id=new_activity.database_id,
                        #     name=sub_indicator.name,
                        # )
                        new_indicator.summation_sub_indicators.add(new_sub_indicator)
                    except:
                        print(sub_indicator.name)
                        continue

            new_indicator.save()


def get_new_indicator_activity(activity, db_destination):
    from internos.activityinfo.models import Activity

    return Activity.objects.get(
        ai_id=activity.ai_id,
        ai_form_id=activity.ai_form_id,
        name=activity.name,
        database_id=db_destination,
        category=activity.category
    )


def get_new_indicator(indicator, activity):
    from internos.activityinfo.models import Indicator

    return Indicator.objects.get(
        ai_id=indicator.ai_id,
        ai_indicator=indicator.ai_indicator,
        activity_id=activity.id,
        name=indicator.name
    )
