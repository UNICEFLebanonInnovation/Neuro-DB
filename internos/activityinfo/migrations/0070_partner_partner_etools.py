# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2019-03-03 13:04
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('etools', '0004_auto_20190303_1107'),
        ('activityinfo', '0069_activityreport_partner_ai'),
    ]

    operations = [
        migrations.AddField(
            model_name='partner',
            name='partner_etools',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='etools.PartnerOrganization'),
        ),
    ]
