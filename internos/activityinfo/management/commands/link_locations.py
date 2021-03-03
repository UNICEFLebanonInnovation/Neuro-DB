__author__ = 'achamseddine'

from django.core.management.base import BaseCommand
from internos.activityinfo.tasks import link_partners


class Command(BaseCommand):
    help = 'link_partners'

    def handle(self, *args, **options):
        link_partners()
