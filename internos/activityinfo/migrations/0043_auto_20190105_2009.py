# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2019-01-05 20:09
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('activityinfo', '0042_indicatortag'),
    ]

    operations = [
        migrations.AlterField(
            model_name='indicator',
            name='tag_age',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='activityinfo.IndicatorTag'),
        ),
        migrations.AlterField(
            model_name='indicator',
            name='tag_disability',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='activityinfo.IndicatorTag'),
        ),
        migrations.AlterField(
            model_name='indicator',
            name='tag_gender',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='activityinfo.IndicatorTag'),
        ),
        migrations.AlterField(
            model_name='indicator',
            name='tag_nationality',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='activityinfo.IndicatorTag'),
        ),
    ]