# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-12-11 20:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activityinfo', '0025_activityreport_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='indicator',
            name='ai_id',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]