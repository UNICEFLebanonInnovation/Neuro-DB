# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-05-25 21:30
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activityinfo', '0151_auto_20200526_0029'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='activityreport',
            name='support_covid',
        ),
        migrations.RemoveField(
            model_name='liveactivityreport',
            name='support_covid',
        ),
    ]
