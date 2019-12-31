__author__ = 'achamseddine'

from django.core.management.base import BaseCommand
from internos.etools.tasks import sync_individual_partner_data


class Command(BaseCommand):
    help = 'sync_individual_intervention_data'

    def handle(self, *args, **options):
        sync_individual_partner_data()
