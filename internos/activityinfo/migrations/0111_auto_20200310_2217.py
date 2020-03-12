# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-03-10 20:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activityinfo', '0110_partner_year'),
    ]

    operations = [
        migrations.AddField(
            model_name='partner',
            name='ai_partner_id',
            field=models.CharField(blank=True, max_length=254),
        ),
        migrations.AlterField(
            model_name='partner',
            name='ai_id',
            field=models.PositiveIntegerField(blank=True),
        ),
    ]