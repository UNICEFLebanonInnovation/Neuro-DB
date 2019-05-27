
import json
import logging

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
def generate_indicators_number():
    from internos.activityinfo.models import Indicator

    for indicator in Indicator.objects.all():
        indicator.ai_indicator = indicator.get_ai_indicator
        indicator.save()


@app.task
def import_data_and_generate_monthly_report():
    from internos.activityinfo.models import Database
    from .utils import import_data_via_r_script, link_indicators_data, calculate_indicators_values, calculate_indicators_tags

    databases = Database.objects.filter(reporting_year__current=True)
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

    databases = Database.objects.filter(reporting_year__current=True)
    if database:
        databases = databases.filter(ai_id=database)

    for db in databases:
        print(db.name)
        print('1. Import report: '+db.name)
        import_data_via_r_script(db, report_type='live')
        print('2. Link data: ' + db.name)
        link_indicators_data(db, report_type='live')
        print('3. Calculate indicator values')
        calculate_indicators_values(db, report_type='live')


@app.task
def copy_indicators_values_to_hpm():
    from internos.activityinfo.models import Indicator

    indicators = Indicator.objects.all()

    for indicator in indicators:
        indicator.values_hpm = indicator.values
        indicator.save()


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
