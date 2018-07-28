__author__ = 'achamseddine'

import json
from django.core.management.base import BaseCommand


class Client:
    pass


class Command(BaseCommand):
    help = 'import_activityinfo_data'

    def handle(self, *args, **options):
        db = Client()
        from internos.activityinfo.client import ActivityInfoClient
        client = ActivityInfoClient()

        print("Fetching database schema...")
        db.schema = client.get_database(8072)
        # print(json.dumps(db.schema))

        # activity = client.get_activity(2142704494)
        # print(json.dumps(activity))

        # indicator = client.get_indicator(1869737822)
        # print(json.dumps(indicator))

        # attribute = client.get_attribute(228220327)
        # print(json.dumps(attribute))

        # partner = client.get_partner(5)
        # print(json.dumps(partner))

        # monthly_report = client.get_monthly_reports_for_site(22742947)
        # print(monthly_report)
        # print(json.dumps(monthly_report))

        # sites = client.get_sites(8072, 5, 2142704494, 1869737822, 228220327)
        sites = client.get_sites(database=8072)
        sites = client.get_sites(database=8072, indicator=1869737822)
        # sites = client.get_sites(8072, 5)
        print(json.dumps(sites))

        # print("Fetching administrative levels...")
        # adminlist = client.get_admin_levels(db.schema['country']['id'])
        # print(adminlist)

