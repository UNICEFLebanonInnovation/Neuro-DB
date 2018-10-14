__author__ = 'achamseddine'

from django.contrib import admin

from . import models


admin.site.site_header = 'Neuro-DB'


class ImportLogAdmin(admin.ModelAdmin):
    list_filter = (
        'object_type',
        'year',
        'month',
    )
    list_display = (
        'object_id',
        'object_name',
        'object_type',
        'year',
        'month',
        'status'
    )


admin.site.register(models.ImportLog, ImportLogAdmin)
