__author__ = 'achamseddine'

from django.core.management.base import BaseCommand
from internos.backends.tasks import read_docx


class Command(BaseCommand):
    help = 'read_docx'

    def handle(self, *args, **options):
        read_docx()
