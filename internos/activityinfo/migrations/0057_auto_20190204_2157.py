# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2019-02-04 21:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activityinfo', '0056_auto_20190204_2157'),
    ]

    operations = [
        migrations.AlterField(
            model_name='indicator',
            name='sequence',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
