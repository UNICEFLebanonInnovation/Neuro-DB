__author__ = 'achamseddine'

from django.core.management.base import BaseCommand

from internos.winterization.tasks import cleanup_old_data


class Command(BaseCommand):
    help = 'Cleanup winter old data'

    def handle(self, *args, **options):
        cleanup_old_data()
