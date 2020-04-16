# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import ItemCategory, Item, EconomicReporting
from .forms import EconomicReportingForm


@admin.register(ItemCategory)
class ItemCategoryAdmin(admin.ModelAdmin):
    list_filter = (
        'reporting_period',
    )
    search_fields = (
        'name',
    )
    list_display = (
        'name',
        'reporting_period',
    )


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_filter = (
        'category',
    )
    search_fields = (
        'name',
    )
    list_display = (
        'name',
        'category',
    )


@admin.register(EconomicReporting)
class EconomicReportingAdmin(admin.ModelAdmin):
    form = EconomicReportingForm
    list_filter = (
        'item',
        'category',
        'category__reporting_period',
    )
    search_fields = (
        'item__name',
        'category__name',
    )
    fields = (
        'category',
        'item',
        'reporting_date',
        'item_price',
    )
    list_display = (
        'category_reporting_period',
        'category',
        'item',
        'reporting_date',
        'item_price',
    )
