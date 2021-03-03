__author__ = 'achamseddine'

from django.core.management.base import BaseCommand

from internos.winterization.tasks import calculate_disaggregation


class Command(BaseCommand):
    help = 'Calculate disaggregation'

    def handle(self, *args, **options):
        calculate_disaggregation()
