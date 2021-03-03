# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-11-23 08:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('winterization', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Programme',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.CharField(max_length=45)),
                ('db_url', models.CharField(max_length=750)),
                ('db_username', models.CharField(max_length=100)),
                ('db_pwd', models.CharField(max_length=750)),
            ],
        ),
    ]
