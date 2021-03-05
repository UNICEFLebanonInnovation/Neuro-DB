# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-05-13 01:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0006_auto_20200427_2124'),
    ]

    operations = [
        migrations.AddField(
            model_name='economicreporting',
            name='source_text',
            field=models.CharField(blank=True, max_length=1500, null=True),
        ),
        migrations.AddField(
            model_name='economicreporting',
            name='source_url',
            field=models.URLField(blank=True, max_length=1500, null=True),
        ),
    ]