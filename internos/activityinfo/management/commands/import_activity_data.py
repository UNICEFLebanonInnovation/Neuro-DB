__author__ = 'achamseddine'

from django.core.management.base import BaseCommand
from internos.activityinfo.tasks import import_activity_data


class Command(BaseCommand):
    help = 'import_activity_data'

    def handle(self, *args, **options):
        import_activity_data()
