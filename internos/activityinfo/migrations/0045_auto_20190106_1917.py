# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2019-01-06 19:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activityinfo', '0044_indicatortag_tag_field'),
    ]

    operations = [
        migrations.AlterField(
            model_name='database',
            name='dashboard_link',
            field=models.URLField(blank=True, max_length=1500, null=True),
        ),
    ]
