__author__ = 'achamseddine'

from django.core.management.base import BaseCommand
from internos.activityinfo.tasks import import_data_and_generate_monthly_report_sector


class Command(BaseCommand):
    help = 'import_data_and_generate_monthly_report_sector'

    def handle(self, *args, **options):
        import_data_and_generate_monthly_report_sector()
