# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-07-24 11:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activityinfo', '0003_activityreport'),
    ]

    operations = [
        migrations.AddField(
            model_name='activityreport',
            name='governorate',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]
