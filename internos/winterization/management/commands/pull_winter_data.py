__author__ = 'achamseddine'

from django.core.management.base import BaseCommand

from internos.winterization.tasks import import_docs


class Command(BaseCommand):
    help = 'Pull winter data from CouchBase'

    def handle(self, *args, **options):
        import_docs()
