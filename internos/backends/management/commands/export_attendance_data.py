__author__ = 'achamseddine'

from django.core.management.base import BaseCommand

from internos.backends.tasks import export_attendance_data


class Command(BaseCommand):
    help = 'export_attendance_data'

    def handle(self, *args, **options):
        export_attendance_data()
