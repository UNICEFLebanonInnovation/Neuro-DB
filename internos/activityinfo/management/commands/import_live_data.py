__author__ = 'achamseddine'

from django.core.management.base import BaseCommand
from internos.activityinfo.tasks import import_live_data


class Command(BaseCommand):
    help = 'Import live indicator values'

    def handle(self, *args, **options):
        import_live_data()
