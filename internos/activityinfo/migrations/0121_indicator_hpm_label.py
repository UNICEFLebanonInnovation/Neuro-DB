# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-03-21 00:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activityinfo', '0120_auto_20200319_1805'),
    ]

    operations = [
        migrations.AddField(
            model_name='indicator',
            name='hpm_label',
            field=models.CharField(blank=True, max_length=5000, null=True),
        ),
    ]