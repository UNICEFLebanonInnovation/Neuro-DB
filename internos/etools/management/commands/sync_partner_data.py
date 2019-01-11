__author__ = 'achamseddine'

from django.core.management.base import BaseCommand
from internos.etools.utils import sync_partner_data


class Command(BaseCommand):
    help = 'read_form_data'

    def handle(self, *args, **options):
        sync_partner_data()
