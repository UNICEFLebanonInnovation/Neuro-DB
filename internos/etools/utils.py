from supplies_platform.taskapp.celery import app

import json
import httplib
import datetime
from time import mktime
from django.core.serializers.json import DjangoJSONEncoder


def sync_partner_data():
    partners = get_data('etools.unicef.org', '/api/v2/partners/', 'Token: 36f06547a4b930c6608e503db49f1e45305351c2')
    print(partners)


def get_data(url, apifunc, token, protocol='HTTPS'):

    # headers = {"Content-type": "application/json", "Authorization": token}
    headers = {"Content-type": "application/json", "X-CSRFToken": 'oeN06eH7uRQp7z9D2m67l0wGcUdC0yub'}

    if protocol == 'HTTPS':
        conn = httplib.HTTPSConnection(url)
    else:
        conn = httplib.HTTPConnection(url)
    conn.request('GET', apifunc, "", headers)
    response = conn.getresponse()
    result = response.read()
    print(response)
    print(result)

    if not response.status == 200:
        if response.status == 400 or response.status == 403:
            raise Exception(str(response.status) + response.reason + response.read())
        else:
            raise Exception(str(response.status) + response.reason)

    conn.close()

    return result


def link_partner_to_partnership():
    from supplies_platform.partners.models import PartnerOrganization, PCA

    partnerships = PCA.objects.all()

    for pca in partnerships:
        try:
            partner = PartnerOrganization.objects.get(name=pca.partner_name)
            pca.partner = partner
            pca.save()
        except Exception as ex:
            continue
