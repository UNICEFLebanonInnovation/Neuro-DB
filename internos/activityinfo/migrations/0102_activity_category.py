# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-02-04 10:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activityinfo', '0101_indicator_tag_programme'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='category',
            field=models.CharField(blank=True, max_length=254, null=True),
        ),
    ]