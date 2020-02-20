__author__ = 'achamseddine'

from django.core.management.base import BaseCommand
from internos.activityinfo.tasks import change_indicators_code


class Command(BaseCommand):
    help = 'change_indicators_code'

    def handle(self, *args, **options):
        change_indicators_code()
