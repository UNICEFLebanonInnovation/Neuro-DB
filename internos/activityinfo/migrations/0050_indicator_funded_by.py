# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2019-01-17 17:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activityinfo', '0049_auto_20190116_2245'),
    ]

    operations = [
        migrations.AddField(
            model_name='indicator',
            name='funded_by',
            field=models.CharField(blank=True, max_length=254, null=True),
        ),
    ]
