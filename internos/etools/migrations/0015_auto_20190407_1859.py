# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-04-07 18:59
from __future__ import unicode_literals

import django.contrib.postgres.fields
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('etools', '0014_engagement_unique_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='engagement',
            name='po_item',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='engagement',
            name='staff_members',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=200), blank=True, null=True, size=None),
        ),
        migrations.RemoveField(
            model_name='engagement',
            name='authorized_officers',
        ),
        migrations.AddField(
            model_name='engagement',
            name='authorized_officers',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=200), blank=True, null=True, size=None),
        ),
    ]
