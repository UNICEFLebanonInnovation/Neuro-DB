# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-04-23 14:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('etools', '0026_pca_end_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='engagement',
            name='displayed_name',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
