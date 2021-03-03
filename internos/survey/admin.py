# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from import_export import resources, fields
from import_export import fields
from djmoney.money import Money
#from reversion.admin import VersionAdmin
from import_export.admin import ImportExportModelAdmin
from django.contrib import admin

from .models import ItemCategory, Item, EconomicReporting, MonitoringReporting, LASER, Map, Research
from .forms import EconomicReportingForm, MonitoringReportingForm, ResearchForm


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
            'reporting_item_id',
            'reporting_date',
            'price_amount',
            'price_currency'
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
        'source_text',
        'source_url',
    )
    list_display = (
        'reporting_date',
        'category',
        'item',
        'item_price',
        'category_reporting_period',
    )

    actions = [
        'update_money_field',
        'update_price_fields',
        'update_item_id',
        'update_reporting_item_id'
    ]

    def update_money_field(self, request,queryset):
        for item in queryset:
            item.item_price = Money(float(item.price_amount), item.price_currency)
            item.save()

    def update_price_fields(self, request,queryset):
        for item in queryset:
            item.price_amount = item.item_price.amount
            item.price_currency = item.item_price.currency
            item.save()

    def update_item_id(self, request,queryset):
        for item in queryset:
            item.item_id = int(item.reporting_item_id)
            item.save()

    def update_reporting_item_id(self, request,queryset):
        for item in queryset:
            item.reporting_item_id = item.item.id
            item.save()


class MonitoringReportingResource(resources.ModelResource):

    class Meta:
        model = MonitoringReporting
        fields = (
            'id',
            'category',
            'item',
            'reporting_date',
            'number',
            'source_text',
            'source_url'
        )
        export_order = fields


@admin.register(MonitoringReporting)
class MonitoringReportingAdmin(ImportExportModelAdmin):
    resource_class = MonitoringReportingResource
    form = MonitoringReportingForm
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
        'number',
        'source_text',
        'source_url',
    )
    list_display = (
        'reporting_date',
        'category',
        'item',
        'number',
        'category_reporting_period',
    )


class LASERResource(resources.ModelResource):
    class Meta:
        model = LASER
        fields = (
            'id',
            'laser_id',
            'organization',
            'focal_point_contact',
            'title',
            'description',
            'status',
            'population_targeted',
            'sectors_covered',
            'report_link',
            'required_followup',
            'published_date',
            'publication_date',
            'estimated_cost',
            'category',
            'evaluation_type',
            'geographical_focus',
            'UNSF_outcome',
            'section'
        )
        export_order = fields


@admin.register(LASER)
class LASERAdmin(ImportExportModelAdmin):
    resource_class = LASERResource

    list_display = ('laser_id', 'organization', 'title', 'status',
                    'category', 'section')
    date_hierarchy = 'created'
    list_filter = ('organization', 'status', 'category', 'section')
    # suit_list_filter_horizontal = ('organization', 'status', 'category', 'section')
    # list_select_related = True


class ResearchResource(resources.ModelResource):
    class Meta:
        model = Research
        fields = (
            'research_id',
            'title',
            'publication_year'
            'organizations',
            'researchers',
            'type',
            'main_sector',
            'geographical_coverage',
            'description',
            'report_link',
            'recommendations',
            'planned_actions',
        )
        export_order = fields


@admin.register(Research)
class ResearchAdmin(ImportExportModelAdmin):
    resource_class = ResearchResource
    form = ResearchForm
    list_display = ('research_id', 'title', 'publication_year',
                    'type', 'main_sector', 'geographical_coverage')
    date_hierarchy = 'created'
    list_filter = ('type', 'main_sector', 'geographical_coverage', 'publication_year')
    search_fields = (
        'research_id',
        'title',
        'organizations',
        'researchers'
    )
    readonly_fields = (
        'research_id',
    )

    fieldsets = [
        ('', {
            # 'classes': ('suit-tab', 'suit-tab-general',),
            'fields': [
                'research_id',
                'title',
                'publication_year',
                'organizations',
                'researchers',
            ]
        }),
        ('', {
            'fields': [
                'type',
                'main_sector',
                'geographical_coverage',
                'description',
                'report_link',
            ]
        }),
        ('', {
            'fields': [
                'recommendations',
            ]
        }),
        ('', {
            'fields': [
                'planned_actions',
            ]
        }),
        ('', {
            'fields': [
                'taken_actions',
            ]
        })
    ]


class MapResource(resources.ModelResource):
    class Meta:
        model = Map
        fields = (
            'id',
            'name',
            'description',
            'link',
            'status',
        )
        export_order = fields


@admin.register(Map)
class MapAdmin(ImportExportModelAdmin):
    resource_class = MapResource

    list_display = ('name', 'description', 'status')
    date_hierarchy = 'created'
    list_filter = ('status', )
