__author__ = 'achamseddine'

from django.core.management.base import BaseCommand
from internos.locations.tasks import sync_location_type_data, sync_locations_data
from internos.etools.tasks import (
    sync_partner_data,
    sync_agreement_data,
    sync_intervention_data,
    sync_trip_data,
    sync_audit_data,
    sync_audit_individual_data,
    sync_action_points_data
)


class Command(BaseCommand):
    help = 'sync_etools_data'

    def handle(self, *args, **options):
        print('sync_partner_data')
        sync_partner_data()
        print('sync_agreement_data')
        sync_agreement_data()
        print('sync_intervention_data')
        sync_intervention_data()
        print('sync_trip_data')
        sync_trip_data()
        print('sync_audit_data')
        sync_audit_data()
        print('sync_action_points_data')
        sync_action_points_data()
