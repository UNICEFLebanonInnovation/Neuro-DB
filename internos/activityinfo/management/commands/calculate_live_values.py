__author__ = 'achamseddine'

from django.core.management.base import BaseCommand
from internos.activityinfo.tasks import calculate_live_values


class Command(BaseCommand):
    help = 'Calculate live indicator values'

    def handle(self, *args, **options):
        calculate_live_values()
