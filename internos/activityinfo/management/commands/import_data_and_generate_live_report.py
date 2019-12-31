__author__ = 'achamseddine'

from django.core.management.base import BaseCommand
from internos.activityinfo.tasks import import_data_and_generate_live_report


class Command(BaseCommand):
    help = 'import_data_and_generate_monthly_report'

    def add_arguments(self, parser):
        parser.add_argument('--database', default=None)

    def handle(self, *args, **options):
        import_data_and_generate_live_report(options['database'])
