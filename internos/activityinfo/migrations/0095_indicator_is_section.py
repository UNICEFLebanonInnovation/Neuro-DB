# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-05-28 12:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activityinfo', '0094_auto_20190528_1131'),
    ]

    operations = [
        migrations.AddField(
            model_name='indicator',
            name='is_section',
            field=models.BooleanField(default=False),
        ),
    ]
