# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-04-15 23:21
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import djmoney.models.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EconomicReporting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.CharField(blank=True, choices=[('2017', '2017'), ('2018', '2018'), ('2019', '2019'), ('2020', '2020'), ('2021', '2021'), ('2022', '2022'), ('2023', '2023'), ('2024', '2024'), ('2025', '2025'), ('2026', '2026'), ('2027', '2027'), ('2028', '2028'), ('2029', '2029'), ('2030', '2030')], max_length=250, null=True)),
                ('reporting_period', models.CharField(choices=[('Weekly', 'Weekly'), ('Twice per week', 'Twice per week'), ('Bi-weekly', 'Bi-weekly'), ('Monthly', 'Monthly')], max_length=250)),
                ('reporting_date', models.DateField()),
                ('item_price_currency', djmoney.models.fields.CurrencyField(choices=[('LBP', 'LBP'), ('USD', 'USD')], default='LBP', editable=False, max_length=3)),
                ('item_price', djmoney.models.fields.MoneyField(decimal_places=2, default_currency=b'LBP', max_digits=14)),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=254)),
            ],
        ),
        migrations.CreateModel(
            name='ItemCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=1500)),
                ('source', models.CharField(max_length=1500)),
                ('description', models.CharField(max_length=1500)),
            ],
        ),
        migrations.AddField(
            model_name='item',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='survey.ItemCategory'),
        ),
        migrations.AddField(
            model_name='economicreporting',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='survey.ItemCategory'),
        ),
        migrations.AddField(
            model_name='economicreporting',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='survey.Item'),
        ),
    ]
