from django.contrib import admin

from import_export import resources, fields
from import_export import fields
from import_export.admin import ImportExportModelAdmin

from .models import Location, LocationType


class LocationResource(resources.ModelResource):
    class Meta:
        model = Location
        fields = (
            'id',
            'name',
            'p_code',
            'type',
            # 'parent',
        )
        export_order = fields


class LocationAdmin(ImportExportModelAdmin):
    resource_class = LocationResource

    search_fields = (
        'name',
    )
    list_display = (
        'name',
        'p_code',
        'type',
        'parent',
    )
    list_filter = (
        'type',
        'parent',
    )


class LocationTypeResource(resources.ModelResource):
    class Meta:
        model = LocationType
        fields = (
            'id',
            'name',
        )
        export_order = fields


class LocationTypeAdmin(ImportExportModelAdmin):
    resource_class = LocationTypeResource

    search_fields = (
        'name',
    )
    list_display = (
        'name',
    )


admin.site.register(LocationType, LocationTypeAdmin)
admin.site.register(Location, LocationAdmin)
