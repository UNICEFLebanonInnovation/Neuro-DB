__author__ = 'achamseddine'

from django.core.management.base import BaseCommand
from internos.activityinfo.tasks import replicate_ai_indicators


class Command(BaseCommand):
    help = 'replicate_ai_indicators'

    def add_arguments(self, parser):
        parser.add_argument('--db_source')
        parser.add_argument('--db_dest')

    def handle(self, *args, **options):
        replicate_ai_indicators(int(options['db_source']), int(options['db_dest']))
