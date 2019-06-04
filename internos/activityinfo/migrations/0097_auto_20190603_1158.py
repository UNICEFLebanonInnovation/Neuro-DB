# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2019-06-03 11:58
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activityinfo', '0096_activity_programme_document'),
    ]

    operations = [
        migrations.AddField(
            model_name='indicator',
            name='cumulative_values_sector',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='indicator',
            name='values_partners_sector',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='indicator',
            name='values_partners_sites_sector',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='indicator',
            name='values_sector',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='indicator',
            name='values_sites_sector',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='indicator',
            name='values_tags_sector',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default={}, null=True),
        ),
    ]