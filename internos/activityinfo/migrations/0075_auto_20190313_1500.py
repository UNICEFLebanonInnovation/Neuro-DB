# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2019-03-13 15:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activityinfo', '0074_auto_20190312_1515'),
    ]

    operations = [
        migrations.AlterField(
            model_name='indicator',
            name='awp_code',
            field=models.CharField(blank=True, max_length=1500, null=True, verbose_name=b'RWP'),
        ),
    ]