# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-05-13 08:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activityinfo', '0140_activityreport_reporting_section'),
    ]

    operations = [
        migrations.AddField(
            model_name='liveactivityreport',
            name='reporting_section',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]