# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2019-01-10 09:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activityinfo', '0045_auto_20190106_1917'),
    ]

    operations = [
        migrations.AddField(
            model_name='indicator',
            name='none_ai_indicator',
            field=models.BooleanField(default=False),
        ),
    ]
