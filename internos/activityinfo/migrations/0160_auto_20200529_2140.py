# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-05-29 21:40
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('etools', '0054_donorfunding_year'),
        ('activityinfo', '0159_indicator_targets'),
    ]

    operations = [
        migrations.AddField(
            model_name='indicator',
            name='project',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='etools.PCA'),
        ),
        migrations.AddField(
            model_name='indicator',
            name='project_code',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='indicator',
            name='project_name',
            field=models.CharField(blank=True, max_length=1500, null=True),
        ),
    ]