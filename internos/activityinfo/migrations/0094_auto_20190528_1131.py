# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-05-28 11:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activityinfo', '0093_database_focal_point_sector'),
    ]

    operations = [
        migrations.AddField(
            model_name='indicator',
            name='status_color_sector',
            field=models.CharField(blank=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='indicator',
            name='status_sector',
            field=models.CharField(blank=True, max_length=254, null=True),
        ),
    ]
