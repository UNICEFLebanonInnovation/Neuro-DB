# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-02-06 11:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activityinfo', '0103_database_db_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='ai_category_id',
            field=models.PositiveIntegerField(null=True, unique=True),
        ),
    ]