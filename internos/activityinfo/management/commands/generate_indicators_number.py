__author__ = 'achamseddine'

from django.core.management.base import BaseCommand
from internos.activityinfo.tasks import generate_indicators_number


class Command(BaseCommand):
    help = 'link_partners'

    def handle(self, *args, **options):
        generate_indicators_number()
