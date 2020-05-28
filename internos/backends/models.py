__author__ = 'achamseddine'

import json
import datetime

from django.db import models
from model_utils.models import TimeStampedModel
from django.contrib.postgres.fields import ArrayField, JSONField
# from django_mysql.models import JSONField


class ImportLog(TimeStampedModel):

    object_id = models.CharField(max_length=25, blank=True, null=True)
    object_name = models.CharField(max_length=254)
    object_type = models.CharField(max_length=25)
    name = models.CharField(max_length=254, blank=True, null=True)
    slug = models.CharField(max_length=254, blank=True, null=True)
    module_name = models.CharField(max_length=254, blank=True, null=True)
    month = models.CharField(max_length=25)
    day = models.CharField(max_length=25, blank=True, null=True)
    year = models.CharField(max_length=25)
    description = models.CharField(max_length=254, blank=True, null=True)
    status = models.BooleanField(default=False)
    result = models.CharField(max_length=25, default='In Progress')
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)

    @staticmethod
    def start(name):
        instance = ImportLog.objects.create(
            name=name,
            slug=name.replace(' ', '_').lower(),
            module_name=name[:name.find(': ')],
            year=datetime.date.today().year,
            month=datetime.date.today().month,
            day=datetime.date.today().day,
            start_date=datetime.datetime.now()
        )
        return instance

    def end(self, result='Success'):
        self.result = result
        self.status = True
        self.end_date = datetime.datetime.now()
        self.save()

    def __unicode__(self):
        return '{} - {}'.format(
            self.object_id,
            self.object_name
        )
