# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2021-03-12 19:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activityinfo', '0170_auto_20210210_2324'),
    ]

    operations = [
        migrations.AddField(
            model_name='database',
            name='last_update_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
