__author__ = 'achamseddine'

from django.core.management.base import BaseCommand
from internos.activityinfo.tasks import migrate_tag


class Command(BaseCommand):
    help = 'migrate_tag'

    def add_arguments(self, parser):
        parser.add_argument('--from_tag', default=None)
        parser.add_argument('--to_tag', default=None)

    def handle(self, *args, **options):
        migrate_tag('tag_nationality_id', options['from_tag'], options['to_tag'])
