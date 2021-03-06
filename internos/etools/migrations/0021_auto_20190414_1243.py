# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-04-14 12:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('etools', '0020_travelactivity_travel'),
    ]

    operations = [
        migrations.AddField(
            model_name='travelactivity',
            name='is_primary_traveler',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='travel',
            name='travel_type',
            field=models.CharField(blank=True, default='Programmatic Visit', max_length=64, verbose_name='Travel Type'),
        ),
        migrations.AlterField(
            model_name='travelactivity',
            name='travel_type',
            field=models.CharField(blank=True, default='Programmatic Visit', max_length=64, verbose_name='Travel Type'),
        ),
    ]
