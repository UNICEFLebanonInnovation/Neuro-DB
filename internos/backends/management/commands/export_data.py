__author__ = 'achamseddine'

from django.core.management.base import BaseCommand

from internos.backends.tasks import export_2ndshift_data

class Command(BaseCommand):
    help = 'Export 2nd shift registrations'

    def handle(self, *args, **options):
        data = export_2ndshift_data()
        file_object = open("enrolment_data.xlsx", "w")
        file_object.write(data)
        file_object.close()
