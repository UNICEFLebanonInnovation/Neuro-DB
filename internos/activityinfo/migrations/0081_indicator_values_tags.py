# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2019-04-17 13:14
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activityinfo', '0080_liveactivityreport'),
    ]

    operations = [
        migrations.AddField(
            model_name='indicator',
            name='values_tags',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default={}, null=True),
        ),
    ]
