# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-02-19 13:19
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0004_auto_20190501_2242'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='location',
            name='parent',
        ),
    ]