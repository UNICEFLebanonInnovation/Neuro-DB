from celery import chain
from django import forms
from django.contrib import admin as basic_admin
from django.contrib.gis import admin
from django.forms import Textarea
from leaflet.admin import LeafletGeoAdmin
from mptt.admin import MPTTModelAdmin
from import_export import resources, fields
from import_export import fields
from import_export.admin import ImportExportModelAdmin
from .models import LocationType, Location


class AutoSizeTextForm(forms.ModelForm):
    """
    Use textarea for name and description fields
    """

    class Meta:
        widgets = {
            'name': Textarea(),
            'description': Textarea(),
        }


class ActiveLocationsFilter(basic_admin.SimpleListFilter):

    title = 'Active Status'
    parameter_name = 'is_active'

    def lookups(self, request, model_admin):

        return [
            (True, 'Active'),
            (False, 'Archived')
        ]

    def queryset(self, request, queryset):
        return queryset.filter(**self.used_parameters)


class LocationResource(resources.ModelResource):
        model = Location
        fields = (
            'id',
            'name',
            'p_code',
            'type',
            # 'parent',
        )
        export_order = fields


class LocationAdmin(LeafletGeoAdmin, MPTTModelAdmin):
# class LocationAdmin(ImportExportModelAdmin):
    save_as = True
    # resource_class = LocationResource
    # form = AutoSizeTextForm
    fields = [
        'name',
        'type',
        'p_code',
        'geom',
        'point',
    ]
    list_display = (
        'name',
        'type',
        'p_code',
        'point',
        'point_lat_long'
        # 'is_active',
    )
    list_filter = (
        'type',
        # ActiveLocationsFilter,
        # 'parent',
    )
    search_fields = ('name', 'p_code',)


admin.site.register(Location, LocationAdmin)
admin.site.register(LocationType)
