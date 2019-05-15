# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-05-15 13:41
from __future__ import unicode_literals

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('etools', '0042_actionpoint_category_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='partnerorganization',
            name='assessments',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=5000), blank=True, null=True, size=None),
        ),
        migrations.AddField(
            model_name='partnerorganization',
            name='core_values_assessment_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='partnerorganization',
            name='core_values_assessments',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=5000), blank=True, null=True, size=None),
        ),
        migrations.AddField(
            model_name='partnerorganization',
            name='flags',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=5000), blank=True, null=True, size=None),
        ),
        migrations.AddField(
            model_name='partnerorganization',
            name='hact_min_requirements',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=5000), blank=True, null=True, size=None),
        ),
        migrations.AddField(
            model_name='partnerorganization',
            name='hact_values',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=5000), blank=True, null=True, size=None),
        ),
        migrations.AddField(
            model_name='partnerorganization',
            name='last_assessment_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='partnerorganization',
            name='net_ct_cy',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='partnerorganization',
            name='planned_engagement',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=5000), blank=True, null=True, size=None),
        ),
        migrations.AddField(
            model_name='partnerorganization',
            name='planned_visits',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=5000), blank=True, null=True, size=None),
        ),
        migrations.AddField(
            model_name='partnerorganization',
            name='reported_cy',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='partnerorganization',
            name='staff_members',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=5000), blank=True, null=True, size=None),
        ),
        migrations.AddField(
            model_name='partnerorganization',
            name='total_ct_cp',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='partnerorganization',
            name='total_ct_cy',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='partnerorganization',
            name='total_ct_ytd',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='partnerorganization',
            name='type_of_assessment',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]
