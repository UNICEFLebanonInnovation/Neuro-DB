__author__ = 'achamseddine'

from django.core.management.base import BaseCommand
from internos.etools.utils import sync_trip_data


class Command(BaseCommand):
    help = 'sync_trip_data'

    def handle(self, *args, **options):
        sync_trip_data()
