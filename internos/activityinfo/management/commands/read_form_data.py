__author__ = 'achamseddine'

from django.core.management.base import BaseCommand
from internos.activityinfo.tasks import read_form_data


class Command(BaseCommand):
    help = 'read_form_data'

    def handle(self, *args, **options):
        read_form_data('hhh')
