# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2019-01-02 14:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activityinfo', '0040_auto_20190102_1438'),
    ]

    operations = [
        migrations.AddField(
            model_name='indicator',
            name='list_header',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='indicator',
            name='type',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]
