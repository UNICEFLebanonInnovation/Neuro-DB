# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-04-16 15:17
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('etools', '0024_engagement_findings_sets'),
    ]

    operations = [
        migrations.AddField(
            model_name='travel',
            name='attachments_sets',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True),
        ),
    ]