__author__ = 'achamseddine'

import json
from datetime import datetime
from django.db import models
from model_utils import Choices
from model_utils.models import TimeStampedModel
from django.contrib.postgres.fields import ArrayField, JSONField

from internos.users.models import Section


class Collection(models.Model):
    name = models.CharField(max_length=254)
    configs = JSONField(blank=True, null=True)

    def __unicode__(self):
        return self.name


class CollectionData(models.Model):
    name = models.CharField(max_length=254)
    data = JSONField(blank=True, null=True)

    def __unicode__(self):
        return self.name
