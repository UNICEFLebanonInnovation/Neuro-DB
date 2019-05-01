__author__ = 'achamseddine'

from django.core.management.base import BaseCommand
from internos.locations.tasks import sync_locations_data


class Command(BaseCommand):
    help = 'sync_locations_data'

    def handle(self, *args, **options):
        sync_locations_data()
