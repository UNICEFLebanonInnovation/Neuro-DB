__author__ = 'achamseddine'

from django.contrib import admin
from suit.admin import RelatedFieldAdmin, get_related_field
import nested_admin
from . import models
from .utils import r_script_command_line, read_data_from_file


admin.site.site_header = 'Neuro-DB'


class PartnerAdmin(admin.ModelAdmin):
    readonly_fields = (
        'ai_id',
        'name',
        'full_name',
        'database'
    )
    list_display = (
        'ai_id',
        'name',
        'full_name',
        'database'
    )


class AttributeGroupInlineAdmin(nested_admin.NestedStackedInline):
    can_delete = False
    model = models.AttributeGroup
    min_num = 0
    max_num = 0
    extra = 0
    fk_name = 'activity'
    fields = (
        'ai_id',
        'name',
        'multiple_allowed',
        'mandatory',
        'choices',
    )
    readonly_fields = (
        'ai_id',
        'name',
        'multiple_allowed',
        'mandatory',
        'choices',
    )

    def choices(self, obj):
        return ", ".join(
            [
                '{} ({})'.format(
                    attribute.name,
                    attribute.ai_id
                )
                for attribute
                in obj.attribute_set.all()
            ]
        )

    def has_add_permission(self, request):
        return False


class IndicatorInlineAdmin(nested_admin.NestedTabularInline):
    can_delete = False
    model = models.Indicator
    verbose_name = 'Indicator'
    verbose_name_plural = 'Indicator'
    min_num = 0
    max_num = 0
    extra = 0
    fk_name = 'activity'
    fields = (
        'ai_id',
        'name',
        'awp_code',
        'units',
    )
    readonly_fields = (
        'ai_id',
        'name',
        'units',
    )

    def has_add_permission(self, request):
        return False


class ActivityInlineAdmin(nested_admin.NestedStackedInline):
    can_delete = False
    model = models.Activity
    verbose_name = 'Activity'
    verbose_name_plural = 'Activities'
    min_num = 0
    max_num = 0
    extra = 0
    fk_name = 'database'
    suit_classes = u'suit-tab suit-tab-activities'
    inline_classes = ("collapse", "open", "grp-collapse", "grp-open",)
    inlines = [
        AttributeGroupInlineAdmin,
        IndicatorInlineAdmin,
    ]
    fields = (
        'ai_id',
        'name',
        'location_type',
    )
    readonly_fields = (
        'ai_id',
        'name',
        'location_type',
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class ActivityAdmin(admin.ModelAdmin):
    # inlines = [
    #     AttributeGroupInlineAdmin,
    #     IndicatorInlineAdmin,
    # ]
    list_display = (
        'name',
        'location_type',
    )
    readonly_fields = (
        'ai_id',
        'name',
        'database',
        'location_type',
    )


class IndicatorAdmin(admin.ModelAdmin):
    # form = AutoSizeTextForm
    search_fields = (
        'ai_id',
    )
    list_filter = (
        'category',
    )
    list_display = (
        'ai_id',
        'activity',
        'awp_code',
        'name',
        'units',
        'category',
    )


class AttributeGroupAdmin(admin.ModelAdmin):
    search_fields = (
        'ai_id',
        'name',
    )
    list_filter = (
        'name',
    )
    list_display = (
        'ai_id',
        'name',
    )


class AttributeAdmin(admin.ModelAdmin):
    # form = AutoSizeTextForm
    search_fields = (
        'ai_id',
        'name',
    )
    list_filter = (
        'name',
    )
    list_display = (
        'ai_id',
        'name',
    )


class PartnerReportAdmin(admin.ModelAdmin):
    list_filter = (
        'pca',
        'indicator',
        'ai_partner',
        'ai_indicator',
        'location',
        'month',
    )
    list_display = (
        'pca',
        'indicator',
        'ai_partner',
        'ai_indicator',
        'location',
        'month',
        'indicator_value',
    )
    readonly_fields = (
        'pca',
        'indicator',
        'ai_partner',
        'ai_indicator',
        'location',
        'month',
        'indicator_value',
    )


class ActivityReportAdmin(RelatedFieldAdmin):
    list_filter = (
        'database',
        'partner_label',
        'governorate',
        'form',
        'form_category',
        # 'indicator_name',
        'funded_by',
        'year',
        'month_name',
    )
    # suit_list_filter_horizontal = (
    #     'database',
    #     'partner_label',
    #     'governorate',
    #     'form',
    #     'form_category',
    #     'indicator_name',
    #     'funded_by',
    # )
    list_select_related = True
    list_display = (
        'database',
        'partner_label',
        'governorate',
        'form',
        'form_category',
        'indicator_name',
        'indicator_value',
        'funded_by',
    )


class DatabaseAdmin(nested_admin.NestedModelAdmin):
    model = models.Database
    inlines = [
        ActivityInlineAdmin,
    ]
    list_display = (
        'ai_id',
        'name',
    )
    readonly_fields = (
        'description',
        'country_name',
        'ai_country_id'
    )
    actions = [
        'import_basic_data',
        'import_data',
        'import_reports'
    ]

    fieldsets = [
        (None, {
            'classes': ('suit-tab', 'suit-tab-general',),
            'fields': [
                'ai_id',
                'name',
                'username',
                'password',
                'section',
                'description',
                'country_name',
                'ai_country_id'
            ]
        }),
        ('Extraction mapping', {
            'classes': ('suit-tab', 'suit-tab-general',),
            'fields': [
                'mapping_extraction1',
                'mapping_extraction2',
                'mapping_extraction3',
            ]
        }),
        ('Activities', {
            'classes': ('suit-tab', 'suit-tab-activities',),
            'fields': [
                # 'ai_id',
                # 'name',
                # 'location_type',
            ]
        }),
    ]

    suit_form_tabs = (
                      ('general', 'Database'),
                      ('activities', 'Activities'),
                    )

    def import_basic_data(self, request, queryset):
        objects = 0
        for db in queryset:
            objects += db.import_data()
        self.message_user(
            request,
            "{} objects created.".format(objects)
        )

    def import_data(self, request, queryset):
        objects = 0
        for db in queryset:
            r_script_command_line('ai_generate_excel.R', db)
            # objects += db.import_data()
        # self.message_user(
        #     request,
        #     "{} objects created.".format(objects)
        # )

    def import_reports(self, request, queryset):
        reports = 0
        for db in queryset:
            read_data_from_file(db.ai_id)
            # reports += db.import_reports()
        # self.message_user(
        #     request,
        #     "{} reports created.".format(reports)
        # )


admin.site.register(models.Database, DatabaseAdmin)
admin.site.register(models.Partner, PartnerAdmin)
admin.site.register(models.Activity, ActivityAdmin)
admin.site.register(models.Indicator, IndicatorAdmin)
admin.site.register(models.AttributeGroup, AttributeGroupAdmin)
admin.site.register(models.Attribute, AttributeAdmin)
admin.site.register(models.ActivityReport, ActivityReportAdmin)

