__author__ = 'achamseddine'

from django.core.management.base import BaseCommand

from internos.backends.tasks import import_2ndshift_data

class Command(BaseCommand):
    help = 'Import 2nd shift registrations'

    def handle(self, *args, **options):
        import_2ndshift_data()
        # data = import_2ndshift_data({'current': True}, return_data=True)
        # file_object = open("enrolment_data.xlsx", "w")
        # file_object.write(data)
        # file_object.close()
