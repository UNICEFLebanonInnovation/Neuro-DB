# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-05-26 18:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activityinfo', '0154_database_support_covid'),
    ]

    operations = [
        migrations.AddField(
            model_name='database',
            name='have_sections',
            field=models.BooleanField(default=False),
        ),
    ]