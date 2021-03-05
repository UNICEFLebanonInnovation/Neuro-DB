# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-05-24 22:25
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('activityinfo', '0087_auto_20190524_1401'),
    ]

    operations = [
        migrations.CreateModel(
            name='Sites',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('partner_name', models.CharField(max_length=650)),
                ('code', models.CharField(max_length=250)),
                ('name', models.CharField(max_length=650)),
                ('longitude', models.CharField(max_length=250)),
                ('latitude', models.CharField(max_length=250)),
                ('activity_name', models.CharField(max_length=2000)),
                ('activity', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='activityinfo.Activity')),
                ('location', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='activityinfo.Locations')),
                ('partner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='activityinfo.Partner')),
            ],
        ),
        migrations.AlterField(
            model_name='activityreport',
            name='location_cadastral',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='activityinfo.AdminLevelEntities'),
        ),
        migrations.AlterField(
            model_name='activityreport',
            name='location_caza',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='activityinfo.AdminLevelEntities'),
        ),
        migrations.AlterField(
            model_name='activityreport',
            name='location_governorate',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='activityinfo.AdminLevels'),
        ),
    ]