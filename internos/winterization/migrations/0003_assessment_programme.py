# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-11-23 09:41
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('winterization', '0002_programme'),
    ]

    operations = [
        migrations.AddField(
            model_name='assessment',
            name='programme',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='winterization.Programme'),
            preserve_default=False,
        ),
    ]
