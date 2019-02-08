__author__ = 'achamseddine'

from django.contrib import admin
from suit.admin import RelatedFieldAdmin, get_related_field
import nested_admin
from import_export import resources, fields
from import_export import fields
from django.db import models
from import_export.admin import ImportExportModelAdmin
from django.contrib.postgres.fields import JSONField
from django_json_widget.widgets import JSONEditorWidget
from django.contrib.admin.widgets import FilteredSelectMultiple
from prettyjson import PrettyJSONWidget
from import_export.widgets import *
from .models import *
from .utils import *
from .forms import DatabaseForm, IndicatorForm, IndicatorFormSet


admin.site.site_header = 'Neuro-DB'


class PartnerResource(resources.ModelResource):

    class Meta:
        model = Partner
        fields = (
            'id',
            'ai_id',
            'name',
            'full_name',
            'database'
        )
        export_order = fields


class PartnerAdmin(ImportExportModelAdmin):
    resource_class = PartnerResource
    list_filter = (
        'database__reporting_year',
        'database',
    )
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
    model = AttributeGroup
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
    model = Indicator
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
    model = Activity
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


class ActivityResource(resources.ModelResource):

    class Meta:
        model = Activity
        fields = (
            'id',
            'ai_id',
            'name',
            'database',
            'location_type',
        )
        export_order = fields


class ActivityAdmin(ImportExportModelAdmin):
    resource_class = ActivityResource
    list_filter = (
        'database__reporting_year',
        'database',
    )
    list_display = (
        'name',
        'database',
        'location_type',
    )
    readonly_fields = (
        'ai_id',
        'name',
        'database',
        'location_type',
    )


class IndicatorResource(resources.ModelResource):

    class Meta:
        model = Indicator
        fields = (
            'id',
            'ai_id',
            'activity',
            'name',
            'label',
            'description',
            'list_header',
            'type',
            'indicator_details',
            'indicator_master',
            'indicator_info',
            'reporting_level',
            'awp_code',
            'target',
            'target_sub_total',
            'cumulative_results',
            'units',
            'category',
            'status',
            'status_color',
            'master_indicator',
            'master_indicator_sub',
            'sub_indicators',
            'summation_sub_indicators',
            'denominator_indicator',
            'numerator_indicator',
            'values',
            'values_gov',
            'values_partners',
            'values_partners_gov',
            'tag_age',
            'tag_gender',
            'tag_nationality',
            'tag_disability',
            'none_ai_indicator',
            'measurement_type',
            'activity__name',
            'activity__database__ai_id',
            'activity__database__name',
            'tag_age__name',
            'tag_gender__name',
            'tag_nationality__name',
            'tag_disability__name',
            'sequence',
            'individual_indicator',
            'explication',
        )


class IndicatorAdmin(ImportExportModelAdmin):
    form = IndicatorForm
    formset = IndicatorFormSet
    resource_class = IndicatorResource
    search_fields = (
        'ai_id',
        'name',
    )
    list_filter = (
        'activity__database__reporting_year',
        'activity__database',
        'master_indicator',
        'master_indicator_sub',
        'individual_indicator',
    )
    suit_list_filter_horizontal = (
        'activity__database__reporting_year',
        'activity__database',
        'master_indicator',
        'master_indicator_sub',
    )
    list_display = (
        'id',
        'ai_id',
        'awp_code',
        'name',
        'target',
        'units',
        'activity',
        'category',
        'sequence',
    )
    filter_horizontal = (
        'sub_indicators',
        'summation_sub_indicators',
        'denominator_summation',
        'numerator_summation',
    )
    list_editable = (
        'awp_code',
        'target',
        'sequence',
    )

    formfield_overrides = {
        JSONField: {'widget': JSONEditorWidget(attrs={'initial': 'parsed'})},
        # models.ManyToManyField: {'widget': FilteredSelectMultiple('indicator', is_stacked=False)}
    }

    fieldsets = [
        ('Basic infos', {
            'classes': ('suit-tab', 'suit-tab-general',),
            'fields': [
                'ai_id',
                'awp_code',
                'name',
                'label',
                'description',
                'explication',
                'activity',
                'list_header',
                'type',
                'reporting_level',
                'target',
                'target_sub_total',
                'cumulative_results',
                'units',
                'category',
                'status',
                'status_color',
                'none_ai_indicator',
                'funded_by',
                'sequence',
            ]
        }),
        ('Tags', {
            'classes': ('suit-tab', 'suit-tab-general',),
            'fields': [
                'tag_age',
                'tag_gender',
                'tag_nationality',
                'tag_disability',
            ]
        }),
        ('Sub indicators', {
            'classes': ('suit-tab', 'suit-tab-general',),
            'fields': [
                'master_indicator',
                'master_indicator_sub',
                'individual_indicator',
                'measurement_type',
                'denominator_indicator',
                'numerator_indicator',
                'sub_indicators',
                'summation_sub_indicators',
                'denominator_summation',
                'numerator_summation',
            ]
        }),
        ('Calculated Values', {
            'classes': ('suit-tab', 'suit-tab-general',),
            'fields': [
                'values',
                'values_gov',
                'values_partners',
                'values_partners_gov',
            ]
        }),
    ]


class AttributeGroupResource(resources.ModelResource):

    class Meta:
        model = AttributeGroup
        fields = (
            'id',
            'ai_id',
            'name',
            'activity',
            'multiple_allowed',
            'mandatory',
        )
        export_order = fields


class AttributeGroupAdmin(ImportExportModelAdmin):
    resource_class = AttributeGroupResource
    search_fields = (
        'ai_id',
        'name',
    )
    list_filter = (
        'activity__database__reporting_year',
        'activity__database',
        'activity',
    )
    list_display = (
        'ai_id',
        'name',
        'activity',
        'multiple_allowed',
        'mandatory',
    )


class AttributeResource(resources.ModelResource):
    class Meta:
        model = Attribute
        fields = (
            'id',
            'ai_id',
            'name',
            'attribute_group',
        )
        export_order = fields


class AttributeAdmin(ImportExportModelAdmin):
    resource_class = AttributeResource
    search_fields = (
        'ai_id',
        'name',
    )
    list_filter = (
        'attribute_group__activity__database__reporting_year',
        'attribute_group__activity__database',
        'attribute_group__activity',
    )
    list_display = (
        'ai_id',
        'name',
        'attribute_group',
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


class ActivityReportResource(resources.ModelResource):

    class Meta:
        model = ActivityReport
        fields = (

        )
        export_order = (
            'id',
            'name',
            'indicator_details',
            'indicator_master',
            'indicator_info',
            'awp_code',
            'target'
        )


class ActivityReportAdmin(RelatedFieldAdmin):
    resources = ActivityReportResource
    list_filter = (
        'start_date',
        'database',
        'partner_label',
        'governorate',
        'form',
        'form_category',
        'funded_by',
        'year',
        'month_name',
        'master_indicator'
    )
    suit_list_filter_horizontal = (
        'start_date',
        'database',
        'partner_label',
        'governorate',
        'form',
        'form_category',
        'funded_by',
        'year',
        'month_name',
    )
    list_select_related = True
    list_display = (
        'id',
        'database',
        'partner_label',
        'governorate',
        'form',
        'form_category',
        'indicator_id',
        'indicator_name',
        'indicator_value',
        'indicator_awp_code',
        'funded_by',
    )
    search_fields = (
        'indicator_id',
        'indicator_name',
        'indicator_awp_code',
    )
    date_hierarchy = 'start_date'


class DatabaseResource(resources.ModelResource):

    class Meta:
        model = Database
        fields = (
            'id',
            'ai_id',
            'name',
            'label',
            'username',
            'password',
            'section',
            'reporting_year',
            'focal_point',
            'mapped_db',
            'is_funded_by_unicef',
            'description',
            'country_name',
            'ai_country_id',
            'dashboard_link',
            'mapping_extraction1',
            'mapping_extraction2',
            'mapping_extraction3',
        )
        export_order = fields


class DatabaseAdmin(ImportExportModelAdmin, nested_admin.NestedModelAdmin):
    form = DatabaseForm
    resources = DatabaseResource
    inlines = [
        # ActivityInlineAdmin,
    ]
    list_filter = (
        'section',
        'reporting_year',
        'is_funded_by_unicef',
    )
    list_display = (
        'ai_id',
        'name',
        'label',
        'reporting_year',
        'focal_point',
        'mapped_db',
        'is_funded_by_unicef',
    )
    readonly_fields = (
        'description',
        'country_name',
        'ai_country_id'
    )
    actions = [
        'import_basic_data',
        'update_basic_data',
        'generate_indicator_tags',
        'import_data',
        'import_reports',
        'import_reports_forced',
        'generate_awp_code',
        'calculate_sum_target',
        'link_indicators_data',
        'reset_indicators_values',
        'calculate_indicators_values',
        'calculate_indicators_status',
        'copy_disaggregated_data',
    ]

    fieldsets = [
        (None, {
            'classes': ('suit-tab', 'suit-tab-general',),
            'fields': [
                'ai_id',
                'name',
                'label',
                'username',
                'password',
                'section',
                'reporting_year',
                'focal_point',
                'mapped_db',
                'is_funded_by_unicef',
                'description',
                'country_name',
                'ai_country_id',
                'dashboard_link',
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

    def update_basic_data(self, request, queryset):
        objects = 0
        for db in queryset:
            objects += db.import_data(import_new=False)
        self.message_user(
            request,
            "{} objects created.".format(objects)
        )

    def generate_indicator_tags(self, request, queryset):
        reports = 0
        for db in queryset:
            reports = generate_indicator_tag(db.ai_id)
        self.message_user(
            request,
            "{} objects updated.".format(reports)
        )

    def import_data(self, request, queryset):
        objects = 0
        for db in queryset:
            r_script_command_line('ai_generate_excel.R', db)
            # objects += db.import_data()
        self.message_user(
            request,
            "{} objects created.".format(objects)
        )

    def import_reports(self, request, queryset):
        reports = 0
        for db in queryset:
            reports = read_data_from_file(db.ai_id)
            # reports += db.import_reports()
        self.message_user(
            request,
            "{} reports created.".format(reports)
        )

    def import_reports_forced(self, request, queryset):
        reports = 0
        for db in queryset:
            reports = read_data_from_file(db.ai_id, True)
        self.message_user(
            request,
            "{} reports created.".format(reports)
        )

    def generate_awp_code(self, request, queryset):
        reports = 0
        for db in queryset:
            reports = generate_indicator_awp_code(db.ai_id)
        self.message_user(
            request,
            "{} reports updated.".format(reports)
        )

    def calculate_sum_target(self, request, queryset):
        reports = 0
        for db in queryset:
            reports = calculate_sum_target(db.id)
        self.message_user(
            request,
            "{} indicators updated.".format(reports)
        )

    def copy_disaggregated_data(self, request, queryset):
        reports = 0
        for db in queryset:
            reports = copy_disaggregated_data(db.ai_id)
        self.message_user(
            request,
            "{} indicators updated.".format(reports)
        )

    def link_indicators_data(self, request, queryset):
        reports = 0
        for db in queryset:
            reports = link_indicators_data(db)
        self.message_user(
            request,
            "{} indicators linked.".format(reports)
        )

    def reset_indicators_values(self, request, queryset):
        reports = 0
        for db in queryset:
            reports = reset_indicators_values(db.ai_id)
        self.message_user(
            request,
            "{} indicators values removed.".format(reports)
        )

    def calculate_indicators_values(self, request, queryset):
        reports = 0
        for db in queryset:
            reports = calculate_indicators_values(db)
        self.message_user(
            request,
            "{} indicators values calculated.".format(reports)
        )

    def calculate_indicators_status(self, request, queryset):
        reports = 0
        for db in queryset:
            reports = calculate_indicators_status(db)
        self.message_user(
            request,
            "{} indicators status calculated.".format(reports)
        )

    formfield_overrides = {
        JSONField: {'widget': JSONEditorWidget(attrs={'initial': 'parsed'})},
    }


class ReportingYearAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'current',
    )


class IndicatorTagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'type',
        'tag_field'
    )


admin.site.register(IndicatorTag, IndicatorTagAdmin)
admin.site.register(ReportingYear, ReportingYearAdmin)
admin.site.register(Database, DatabaseAdmin)
admin.site.register(Partner, PartnerAdmin)
admin.site.register(Activity, ActivityAdmin)
admin.site.register(Indicator, IndicatorAdmin)
admin.site.register(AttributeGroup, AttributeGroupAdmin)
admin.site.register(Attribute, AttributeAdmin)
admin.site.register(ActivityReport, ActivityReportAdmin)

