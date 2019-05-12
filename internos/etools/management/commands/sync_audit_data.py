__author__ = 'achamseddine'

from django.core.management.base import BaseCommand
from internos.etools.tasks import sync_audit_data


class Command(BaseCommand):
    help = 'sync_audit_data'

    def handle(self, *args, **options):
        sync_audit_data()
