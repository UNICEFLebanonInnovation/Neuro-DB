__author__ = 'achamseddine'

from django.core.management.base import BaseCommand
from internos.locations.tasks import sync_location_type_data


class Command(BaseCommand):
    help = 'sync_location_type_data'

    def handle(self, *args, **options):
        sync_location_type_data()
