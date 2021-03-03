# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2019-03-27 11:51
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('activityinfo', '0079_indicator_ai_indicator'),
    ]

    operations = [
        migrations.CreateModel(
            name='LiveActivityReport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('end_date', models.CharField(blank=True, max_length=250, null=True)),
                ('form', models.CharField(blank=True, max_length=1000, null=True)),
                ('form_category', models.CharField(blank=True, max_length=1000, null=True)),
                ('indicator_category', models.CharField(blank=True, max_length=1000, null=True)),
                ('indicator_id', models.CharField(blank=True, max_length=250, null=True)),
                ('indicator_name', models.CharField(blank=True, max_length=1000, null=True)),
                ('indicator_details', models.CharField(blank=True, max_length=1000, null=True)),
                ('indicator_master', models.CharField(blank=True, max_length=250, null=True)),
                ('indicator_info', models.CharField(blank=True, max_length=250, null=True)),
                ('indicator_units', models.CharField(blank=True, max_length=250, null=True)),
                ('indicator_value', models.FloatField(blank=True, null=True)),
                ('indicator_sub_value', models.CharField(blank=True, max_length=250, null=True)),
                ('indicator_awp_code', models.CharField(blank=True, max_length=254, null=True)),
                ('location_adminlevel_cadastral_area', models.CharField(blank=True, max_length=250, null=True)),
                ('location_adminlevel_cadastral_area_code', models.CharField(blank=True, max_length=250, null=True)),
                ('location_adminlevel_caza', models.CharField(blank=True, max_length=250, null=True)),
                ('location_adminlevel_caza_code', models.CharField(blank=True, max_length=250, null=True)),
                ('location_adminlevel_governorate', models.CharField(blank=True, max_length=250, null=True)),
                ('location_adminlevel_governorate_code', models.CharField(blank=True, max_length=250, null=True)),
                ('governorate', models.CharField(blank=True, max_length=250, null=True)),
                ('location_alternate_name', models.CharField(blank=True, max_length=250, null=True)),
                ('location_latitude', models.CharField(blank=True, max_length=250, null=True)),
                ('location_longitude', models.CharField(blank=True, max_length=250, null=True)),
                ('location_name', models.CharField(blank=True, max_length=250, null=True)),
                ('partner_description', models.CharField(blank=True, max_length=250, null=True)),
                ('partner_id', models.CharField(blank=True, max_length=250, null=True)),
                ('partner_label', models.CharField(blank=True, max_length=250, null=True)),
                ('project_description', models.CharField(blank=True, max_length=250, null=True)),
                ('project_label', models.CharField(blank=True, max_length=250, null=True)),
                ('lcrp_appeal', models.CharField(blank=True, max_length=250, null=True)),
                ('funded_by', models.CharField(blank=True, max_length=250, null=True)),
                ('report_id', models.CharField(blank=True, max_length=250, null=True)),
                ('site_id', models.CharField(blank=True, max_length=250, null=True)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('outreach_platform', models.CharField(blank=True, max_length=250, null=True)),
                ('database_id', models.CharField(blank=True, max_length=250, null=True)),
                ('database', models.CharField(blank=True, max_length=250, null=True)),
                ('month', models.CharField(blank=True, max_length=250, null=True)),
                ('day', models.CharField(blank=True, max_length=250, null=True)),
                ('month_name', models.CharField(blank=True, max_length=250, null=True)),
                ('year', models.CharField(blank=True, max_length=250, null=True)),
                ('master_indicator', models.BooleanField(default=False)),
                ('master_indicator_sub', models.BooleanField(default=False)),
                ('order', models.PositiveIntegerField(default=0)),
                ('pending', models.BooleanField(default=False)),
                ('ai_indicator', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='activityinfo.Indicator')),
                ('partner_ai', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='activityinfo.Partner')),
            ],
            options={
                'ordering': ['id'],
            },
        ),
    ]
