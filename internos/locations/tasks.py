from internos.taskapp.celery import app

import json
import httplib
import datetime
from time import mktime
from internos.backends.utils import get_data


def sync_location_type_data():
    from internos.locations.models import LocationType
    instances = get_data('etools.unicef.org', '/api/locations-types/', 'Token 36f06547a4b930c6608e503db49f1e45305351c2')
    instances = json.loads(instances)

    for item in instances:

        instance, new_instance = LocationType.objects.get_or_create(id=int(item['id']))
        instance.name = item['name']
        instance.admin_level = item['admin_level']

        instance.save()


def sync_locations_data():
    from internos.locations.models import Location
    instances = get_data('etools.unicef.org', '/api/locations/', 'Token 36f06547a4b930c6608e503db49f1e45305351c2')
    instances = json.loads(instances)

    for item in instances:

        instance, new_instance = Location.objects.get_or_create(id=int(item['id']))
        try:
            instance.name = item['name']
            instance.p_code = item['p_code']
            instance.type_id = int(item['gateway']['id'])
            instance.parent_id = item['parent']
            instance.point = item['geo_point']

            instance.save()

        except Exception as ex:
            continue
