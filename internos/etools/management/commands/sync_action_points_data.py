__author__ = 'achamseddine'

from django.core.management.base import BaseCommand
from internos.etools.tasks import sync_action_points_data


class Command(BaseCommand):
    help = 'sync_action_points_data'

    def handle(self, *args, **options):
        sync_action_points_data()
