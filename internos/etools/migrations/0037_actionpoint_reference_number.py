# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-05-14 13:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('etools', '0036_auto_20190514_1340'),
    ]

    operations = [
        migrations.AddField(
            model_name='actionpoint',
            name='reference_number',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]