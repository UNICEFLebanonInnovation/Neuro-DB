# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-05-25 21:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activityinfo', '0152_auto_20200526_0030'),
    ]

    operations = [
        migrations.AddField(
            model_name='activityreport',
            name='support_covid',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='liveactivityreport',
            name='support_covid',
            field=models.BooleanField(default=False),
        ),
    ]