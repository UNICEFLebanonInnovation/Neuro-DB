# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-03-11 13:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activityinfo', '0114_auto_20200311_1348'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='partner',
            name='ai_partner_id',
        ),
        migrations.AddField(
            model_name='database',
            name='display',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='partner',
            name='ai_id',
            field=models.CharField(blank=True, max_length=254, null=True),
        ),
    ]