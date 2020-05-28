# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-05-25 21:29
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activityinfo', '0150_merge_20200525_0858'),
    ]

    operations = [
        migrations.AddField(
            model_name='indicator',
            name='values_cumulative_weekly',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default={}, null=True),
        ),
        migrations.AddField(
            model_name='indicator',
            name='values_gov_weekly',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default={}, null=True),
        ),
        migrations.AddField(
            model_name='indicator',
            name='values_partners_gov_weekly',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default={}, null=True),
        ),
        migrations.AddField(
            model_name='indicator',
            name='values_partners_weekly',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default={}, null=True),
        ),
        migrations.AddField(
            model_name='indicator',
            name='values_weekly',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default={}, null=True),
        ),
    ]
