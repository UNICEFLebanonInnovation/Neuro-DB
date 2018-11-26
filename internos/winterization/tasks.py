
import json
import os
import tablib

import requests
from django.conf import settings
from django.db import connection
from requests.auth import HTTPBasicAuth
from import_export.formats import base_formats
from internos.taskapp.celery import app


@app.task
def cleanup_old_data(programme=None):
    from .models import Assessment

    registrations = Assessment.objects.all()
    if programme:
        registrations = registrations.filter(programme=programme)

    objects = registrations.count()
    registrations.delete()
    return objects


def set_docs(docs):

    payload_json = json.dumps(
        {
            'docs': docs,
            'all_or_nothing': True
        }
    )
    path = os.path.join(settings.COUCHBASE_URL, '_bulk_docs')
    response = requests.post(
        path,
        headers={'content-type': 'application/json'},
        auth=HTTPBasicAuth(settings.COUCHBASE_USER, settings.COUCHBASE_PASS),
        data=payload_json,
    )
    return response


@app.task
def set_app_user(username, password):

    user_docs = []
    user_docs.append(
        {
            "_id": username,
            "type": "user",
            "username": username,
            "password": password,
            "organisation": username,
        }
    )

    response = set_docs(user_docs)
    return response.text


@app.task
def import_docs(programme=None, **kwargs):
    """
    Imports docs from couch base
    """
    from .models import Assessment
    from .serializers import AssessmentSerializer

    data = requests.get(
        os.path.join(programme.db_url, '_all_docs?include_docs=true'),
        auth=HTTPBasicAuth(programme.db_username, programme.db_pwd)
    ).json()

    ctr = 0
    for row in data['rows']:
        if 'doc' in row:
            doc = row['doc']
            doc['site_type'] = doc['site-type'] if 'site-type' in doc else ''
            # todo assistance_type fix the return type
            if programme:
                doc['programme'] = programme
            ctr += 1
            instance = Assessment.objects.create(_id=doc['_id'])
            for key in doc:
                if hasattr(instance, key):
                    setattr(instance, key, doc[key])
            instance.save()
            # serializer = AssessmentSerializer(data=doc)
            # if serializer.is_valid():
            #     ctr += 1
            #     instance = serializer.create(validated_data=serializer.validated_data)
            #     instance.save()
            # else:
            #     print(serializer.errors)

    return ctr


@app.task
def calculate_disaggregation(programme=None):
    from .models import Assessment

    queryset = Assessment.objects.filter(child_list__isnull=False)
    if programme:
        queryset = queryset.filter(programme=programme)

    objects = queryset.count()

    for line in queryset:
        data = line.child_list
        line.set_0_to_3_months(find_total(data=data, name='age', value='0 to 3 months'))
        line.set_3_to_12_months(find_total(data=data, name='age', value='3 to 12 months'))
        line.set_1_year_old(find_total(data=data, name='age', value='1 year old'))
        line.set_2_years_old(find_total(data=data, name='age', value='2 years old'))
        line.set_3_years_old(find_total(data=data, name='age', value='3 years old'))
        line.set_4_years_old(find_total(data=data, name='age', value='4 years old'))
        line.set_5_years_old(find_total(data=data, name='age', value='5 years old'))
        line.set_6_years_old(find_total(data=data, name='age', value='6 years old'))
        line.set_7_years_old(find_total(data=data, name='age', value='7 years old'))
        line.set_8_years_old(find_total(data=data, name='age', value='8 years old'))
        line.set_9_years_old(find_total(data=data, name='age', value='9 years old'))
        line.set_10_years_old(find_total(data=data, name='age', value='10 years old'))
        line.set_11_years_old(find_total(data=data, name='age', value='11 years old'))
        line.set_12_years_old(find_total(data=data, name='age', value='12 years old'))
        line.set_13_years_old(find_total(data=data, name='age', value='13 years old'))
        line.set_14_years_old(find_total(data=data, name='age', value='14 years old'))
        line.male = find_total(data=data, name='gender', value='Boy')
        line.female = find_total(data=data, name='gender', value='Girl')
        line.set_3_months_kit(find_total(data=data, name='kit', value='3 months'))
        line.set_12_months_kit(find_total(data=data, name='kit', value='12 months'))
        line.set_2_years_kit(find_total(data=data, name='kit', value='2 years'))
        line.set_3_years_kit(find_total(data=data, name='kit', value='3 years'))
        line.set_5_years_kit(find_total(data=data, name='kit', value='5 years'))
        line.set_7_years_kit(find_total(data=data, name='kit', value='7 years'))
        line.set_9_years_kit(find_total(data=data, name='kit', value='9 years'))
        line.set_12_years_kit(find_total(data=data, name='kit', value='12 years'))
        line.set_14_years_kit(find_total(data=data, name='kit', value='14 years'))
        line.set_3_months_kit_completed(find_total(data=data, name='kit', value='3 months',
                                                   status_condition='COMPLETED'))
        line.set_12_months_kit_completed(find_total(data=data, name='kit', value='12 months',
                                                    status_condition='COMPLETED'))
        line.set_2_years_kit_completed(find_total(data=data, name='kit', value='2 years',
                                                  status_condition='COMPLETED'))
        line.set_3_years_kit_completed(find_total(data=data, name='kit', value='3 years',
                                                  status_condition='COMPLETED'))
        line.set_5_years_kit_completed(find_total(data=data, name='kit', value='5 years',
                                                  status_condition='COMPLETED'))
        line.set_7_years_kit_completed(find_total(data=data, name='kit', value='7 years',
                                                  status_condition='COMPLETED'))
        line.set_9_years_kit_completed(find_total(data=data, name='kit', value='9 years',
                                                  status_condition='COMPLETED'))
        line.set_12_years_kit_completed(find_total(data=data, name='kit', value='12 years',
                                                   status_condition='COMPLETED'))
        line.set_14_years_kit_completed(find_total(data=data, name='kit', value='14 years',
                                                   status_condition='COMPLETED'))

        line.save()

    return objects


def find_total(data, name, value, status_condition=None):
    ctr = 0
    for item in data:
        if status_condition:
            if item['status'] == status_condition and item[name] == value:
                ctr += 1
        elif item[name] == value:
            ctr += 1
    return ctr
