# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-04-07 18:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('etools', '0012_auto_20190407_1756'),
    ]

    operations = [
        migrations.AlterField(
            model_name='engagement',
            name='status',
            field=models.CharField(choices=[('partner_contacted', 'IP Contacted'), ('report_submitted', 'Report Submitted'), ('final', 'Final Report'), ('cancelled', 'Cancelled')], default='partner_contacted', max_length=30, verbose_name='Status'),
        ),
    ]
