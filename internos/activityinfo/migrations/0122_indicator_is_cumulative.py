# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-03-25 22:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activityinfo', '0121_indicator_hpm_label'),
    ]

    operations = [
        migrations.AddField(
            model_name='indicator',
            name='is_Cumulative',
            field=models.BooleanField(default=True),
        ),
    ]
