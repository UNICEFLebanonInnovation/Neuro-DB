# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2021-03-23 20:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activityinfo', '0174_auto_20210322_2125'),
    ]

    operations = [
        migrations.AddField(
            model_name='indicator',
            name='ram_result',
            field=models.PositiveIntegerField(default=0, verbose_name=b'RAM Result'),
        ),
    ]
