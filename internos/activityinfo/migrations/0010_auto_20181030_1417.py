# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-10-30 14:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activityinfo', '0009_auto_20181030_1324'),
    ]

    operations = [
        migrations.AlterField(
            model_name='indicator',
            name='awp_code',
            field=models.CharField(blank=True, max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name='indicator',
            name='reporting_level',
            field=models.CharField(blank=True, max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name='indicator',
            name='status',
            field=models.CharField(blank=True, max_length=254, null=True),
        ),
    ]
