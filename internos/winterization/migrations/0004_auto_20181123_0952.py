# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-11-23 09:52
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('winterization', '0003_assessment_programme'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assessment',
            name='programme',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='winterization.Programme'),
        ),
    ]