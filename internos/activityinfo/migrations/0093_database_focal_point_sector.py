# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-05-28 11:29
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('activityinfo', '0092_auto_20190527_0827'),
    ]

    operations = [
        migrations.AddField(
            model_name='database',
            name='focal_point_sector',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
    ]