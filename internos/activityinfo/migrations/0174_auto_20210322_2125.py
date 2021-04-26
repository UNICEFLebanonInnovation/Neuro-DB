# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2021-03-22 21:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activityinfo', '0173_auto_20210312_1957'),
    ]

    operations = [
        migrations.AddField(
            model_name='indicator',
            name='has_hpm_hac_2_note',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='indicator',
            name='hpm_hac_2_label',
            field=models.CharField(blank=True, max_length=5000, null=True, verbose_name=b'HPM HAC 2 Label'),
        ),
        migrations.AlterField(
            model_name='indicator',
            name='hpm_additional_cumulative',
            field=models.PositiveIntegerField(default=0, verbose_name=b'HPM Cumulative'),
        ),
        migrations.AlterField(
            model_name='indicator',
            name='hpm_hac_2_additional_cumulative',
            field=models.PositiveIntegerField(default=0, verbose_name=b'HPM HAC 2 Cumulative'),
        ),
        migrations.AlterField(
            model_name='indicator',
            name='is_standalone_HAC_2',
            field=models.BooleanField(default=False, verbose_name=b'Is Standalone HAC 2 HPM'),
        ),
    ]