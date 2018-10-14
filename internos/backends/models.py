__author__ = 'achamseddine'

import json

from datetime import datetime
from django.db import models
from model_utils.models import TimeStampedModel
from django.contrib.postgres.fields import ArrayField, JSONField
# from django_mysql.models import JSONField


class ImportLog(TimeStampedModel):

    object_id = models.CharField(max_length=25)
    object_name = models.CharField(max_length=254)
    object_type = models.CharField(max_length=25)
    month = models.CharField(max_length=25)
    year = models.CharField(max_length=25)
    description = models.CharField(max_length=254, blank=True, null=True)
    status = models.BooleanField(default=True)

    def __unicode__(self):
        return '{} - {}'.format(
            self.object_id,
            self.object_name
        )
