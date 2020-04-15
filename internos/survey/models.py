# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from djmoney.models.fields import MoneyField
from django.db import models
from model_utils import Choices
from model_utils.models import TimeStampedModel
from django.contrib.postgres.fields import ArrayField, JSONField


class ItemCategory(models.Model):
    name = models.CharField(max_length=1500)
    source = models.CharField(max_length=1500)
    description = models.CharField(max_length=1500)
    reporting_period = models.CharField(
        max_length=250,
        blank=False,
        null=False,
        choices=Choices(
            ('Weekly', 'Weekly'),
            ('Twice per week', 'Twice per week'),
            ('Bi-weekly', 'Bi-weekly'),
            ('Monthly', 'Monthly'),
        )
    )

    def __unicode__(self):
        return self.name


class Item(models.Model):
    name = models.CharField(max_length=254)
    category = models.ForeignKey(
        ItemCategory,
        blank=True, null=True,
        related_name='+',
    )

    def __unicode__(self):
        return self.name


class EconomicReporting(models.Model):

    category = models.ForeignKey(
        ItemCategory,
        blank=False, null=False,
        related_name='+',
    )
    item = models.ForeignKey(
        Item,
        blank=False, null=False,
        related_name='+',
    )

    year = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        choices=Choices(
            ('2017', '2017'),
            ('2018', '2018'),
            ('2019', '2019'),
            ('2020', '2020'),
            ('2021', '2021'),
            ('2022', '2022'),
            ('2023', '2023'),
            ('2024', '2024'),
            ('2025', '2025'),
            ('2026', '2026'),
            ('2027', '2027'),
            ('2028', '2028'),
            ('2029', '2029'),
            ('2030', '2030'),
        )
    )

    reporting_period = models.CharField(
        max_length=250,
        blank=False,
        null=False,
        choices=Choices(
            ('Weekly', 'Weekly'),
            ('Twice per week', 'Twice per week'),
            ('Bi-weekly', 'Bi-weekly'),
            ('Monthly', 'Monthly'),
        )
    )

    reporting_date = models.DateField(blank=False, null=False)

    item_price = MoneyField(max_digits=14, decimal_places=2, default_currency='LBP')

    @property
    def category_reporting_period(self):
        if self.category:
            return self.category.reporting_period
        return ''

    def __unicode__(self):
        return str(self.id)
