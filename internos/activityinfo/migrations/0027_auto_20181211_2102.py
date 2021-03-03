# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-12-11 21:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activityinfo', '0026_auto_20181211_2053'),
    ]

    operations = [
        migrations.AlterField(
            model_name='indicator',
            name='sub_indicators',
            field=models.ManyToManyField(blank=True, related_name='_indicator_sub_indicators_+', to='activityinfo.Indicator'),
        ),
        migrations.AlterField(
            model_name='indicator',
            name='summation_sub_indicators',
            field=models.ManyToManyField(blank=True, related_name='_indicator_summation_sub_indicators_+', to='activityinfo.Indicator'),
        ),
    ]
