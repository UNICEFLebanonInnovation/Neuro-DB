# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-05-24 15:38
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activityinfo', '0147_remove_indicator_related_indicator'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='activityreport',
            name='support_covid',
        ),
    ]
