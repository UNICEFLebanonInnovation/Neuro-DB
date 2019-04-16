__author__ = 'achamseddine'

from django.core.management.base import BaseCommand
from internos.etools.utils import sync_trip_individual_data


class Command(BaseCommand):
    help = 'sync_trip_individual_data'

    def handle(self, *args, **options):
        from internos.etools.models import Travel
        travels = Travel.objects.all()
        # travels = Travel.objects.filter()
        for instance in travels.iterator():
            # print(instance.id)
            sync_trip_individual_data(instance)
