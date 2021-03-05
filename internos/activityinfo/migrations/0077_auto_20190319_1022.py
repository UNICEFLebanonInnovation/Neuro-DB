# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2019-03-19 10:22
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activityinfo', '0076_auto_20190319_1015'),
    ]

    operations = [
        migrations.AlterField(
            model_name='indicator',
            name='cumulative_values_hpm',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default={}, null=True),
        ),
        migrations.AlterField(
            model_name='indicator',
            name='values_hpm',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default={}, null=True),
        ),
    ]