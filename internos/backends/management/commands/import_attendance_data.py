__author__ = 'achamseddine'

from django.core.management.base import BaseCommand

from internos.backends.tasks import import_attendance_data


class Command(BaseCommand):
    help = 'import_attendance_data'

    def handle(self, *args, **options):
        import_attendance_data()
