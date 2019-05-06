# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-05-06 08:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('etools', '0028_auto_20190506_0813'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pca',
            name='status',
            field=models.CharField(blank=True, default='in_process', help_text='In Process = In discussion with partner, Active = Currently ongoing, Implemented = completed, Cancelled = cancelled or not approved', max_length=32),
        ),
    ]