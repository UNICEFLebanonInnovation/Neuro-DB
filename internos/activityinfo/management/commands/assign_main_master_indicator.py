__author__ = 'achamseddine'

from django.core.management.base import BaseCommand
from internos.activityinfo.utils import assign_main_master_indicator


class Command(BaseCommand):
    help = 'assign_main_master_indicator'

    def handle(self, *args, **options):
        assign_main_master_indicator()
