# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2019-02-10 01:25
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activityinfo', '0062_auto_20190209_0441'),
    ]

    operations = [
        migrations.AddField(
            model_name='indicator',
            name='cumulative_values',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True),
        ),
    ]
