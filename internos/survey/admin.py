# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from import_export import resources, fields
from import_export import fields
from import_export.admin import ImportExportModelAdmin
from django.contrib import admin

from .models import ItemCategory, Item, EconomicReporting
from .forms import EconomicReportingForm


class ItemCategoryResource(resources.ModelResource):

    class Meta:
        model = ItemCategory
        fields = (
            'id',
            'name',
            'source',
            'description',
            'reporting_period'
        )
        export_order = fields


@admin.register(ItemCategory)
class ItemCategoryAdmin(ImportExportModelAdmin):
    resource_class = ItemCategoryResource
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


class ItemResource(resources.ModelResource):

    class Meta:
        model = Item
        fields = (
            'id',
            'name',
            'category',
        )
        export_order = fields


@admin.register(Item)
class ItemAdmin(ImportExportModelAdmin):
    resource_class = ItemResource
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


class EconomicReportingResource(resources.ModelResource):

    class Meta:
        model = EconomicReporting
        fields = (
            'id',
            'category',
            'item',
            'reporting_date',
            'item_price'
        )
        export_order = fields


@admin.register(EconomicReporting)
class EconomicReportingAdmin(ImportExportModelAdmin):
    resource_class = EconomicReportingResource
    form = EconomicReportingForm
    list_filter = (
        'item',
        'category',
        'category__reporting_period',
    )
    suit_list_filter_horizontal = (
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
