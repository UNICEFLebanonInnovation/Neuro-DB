__author__ = 'achamseddine'

from django.contrib import admin

from . import models


admin.site.site_header = 'Neuro-DB'


class ImportLogAdmin(admin.ModelAdmin):

    list_filter = (
        'name',
        'module_name',
        'year',
        'month',
    )
    list_display = (
        'module_name',
        'name',
        'slug',
        'start_date',
        'end_date',
        'status',
        'result',
    )


admin.site.register(models.ImportLog, ImportLogAdmin)
