__author__ = 'achamseddine'

from django.core.management.base import BaseCommand
from internos.activityinfo.tasks import copy_indicators_values_to_hpm


class Command(BaseCommand):
    help = 'copy_indicators_values_to_hpm'

    def handle(self, *args, **options):
        copy_indicators_values_to_hpm()
