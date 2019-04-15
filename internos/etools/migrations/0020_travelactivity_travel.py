# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-04-13 21:45
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('etools', '0019_travel_travel_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='travelactivity',
            name='travel',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='travels', to='etools.Travel', verbose_name='Travels'),
        ),
    ]