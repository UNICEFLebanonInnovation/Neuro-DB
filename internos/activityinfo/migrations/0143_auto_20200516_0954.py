# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-05-16 06:54
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activityinfo', '0142_auto_20200515_1613'),
    ]

    operations = [
        migrations.AddField(
            model_name='indicator',
            name='values_sections_gov_live',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='indicator',
            name='values_sections_live',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='indicator',
            name='values_sections_partners_gov_live',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='indicator',
            name='values_sections_partners_live',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True),
        ),
    ]