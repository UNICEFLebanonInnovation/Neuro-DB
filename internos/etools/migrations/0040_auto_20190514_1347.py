# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-05-14 13:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('etools', '0039_actionpoint_status_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='actionpoint',
            name='date_of_completion',
            field=models.DateField(blank=True, null=True),
        ),
    ]