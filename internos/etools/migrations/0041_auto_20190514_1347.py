# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-05-14 13:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('etools', '0040_auto_20190514_1347'),
    ]

    operations = [
        migrations.AlterField(
            model_name='actionpoint',
            name='date_of_completion',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='actionpoint',
            name='status_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]