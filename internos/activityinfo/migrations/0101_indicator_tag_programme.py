# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-08-13 08:05
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('activityinfo', '0100_indicator_support_disability'),
    ]

    operations = [
        migrations.AddField(
            model_name='indicator',
            name='tag_programme',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='activityinfo.IndicatorTag'),
        ),
    ]
