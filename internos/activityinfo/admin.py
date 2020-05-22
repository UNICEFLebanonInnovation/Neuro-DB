__author__ = 'achamseddine'

from django.contrib import admin
from suit.admin import RelatedFieldAdmin, get_related_field
import nested_admin
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from django.contrib.postgres.fields import JSONField
from django_json_widget.widgets import JSONEditorWidget
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
        # 'database__reporting_year',
        # 'database',
        'year',
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
        'year',
        'database',
        'partner_etools',
    )
    search_fields = (
        'name',
        'full_name',
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


class PartnerInlineAdmin(nested_admin.NestedTabularInline):
    model = IndicatorPartner
    verbose_name = 'Partner'
    verbose_name_plural = 'Partners'
    min_num = 0
    max_num = 99
    extra = 0
    fk_name = 'ai_indicator'
    suit_classes = u'suit-tab suit-tab-partner-targets'
    inline_classes = ("collapse", "open", "grp-collapse", "grp-open",)
    fields = (
        'partner',
        'target',
    )


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
        'category',
        'location_type',
        'programme_document'
    )
    # list_editable = (
    #     'programme_document',
    # )
    readonly_fields = (
        'ai_id',
        # 'name',
        'database',
        'category',
        'location_type',
    )


class TagAgeFilter(admin.SimpleListFilter):
    title = 'Tag Age'

    parameter_name = 'tag_age'

    def lookups(self, request, model_admin):
        return ((l.id, l.name) for l in IndicatorTag.objects.filter(type='age'))

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(tag_age_id__exact=self.value())
        return queryset


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
            'target_sector',
            'target_sub_total',
            'units',
            'category',
            'status',
            'status_color',
            'master_indicator',
            'master_indicator_sub',
            'master_indicator_sub_sub',
            'sub_indicators',
            'summation_sub_indicators',
            'denominator_indicator',
            'numerator_indicator',
            'values',
            'values_hpm',
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
            'calculated_indicator',
            'calculated_percentage',
            'cumulative_values',
            'cumulative_values_hpm',
            'hpm_indicator',
            'separator_indicator',
            'values_live',
            'values_gov_live',
            'values_partners_live',
            'values_partners_gov_live',
            'cumulative_values_live',
            'values_hpm',
            'values_tags',
            'cumulative_values_hpm',
        )


class IndicatorAdmin(ImportExportModelAdmin, nested_admin.NestedModelAdmin):
    form = IndicatorForm
    # formset =
    inlines = [
        PartnerInlineAdmin,
    ]
    resource_class = IndicatorResource
    search_fields = (
        'ai_indicator',
        'name',
    )
    list_filter = (
        'activity__database__reporting_year',
        'activity__database',
        'activity',
        'master_indicator',
        'master_indicator_sub',
        'master_indicator_sub_sub',
        'individual_indicator',
        'calculated_indicator',
        'hpm_indicator',
        'separator_indicator',
        # 'tag_gender',
        # 'tag_age',
        # 'tag_nationality',
        # 'tag_disability',
        # 'tag_programme',
    )
    suit_list_filter_horizontal = (
        'activity__database__reporting_year',
        'activity__database',
        'activity',
        'master_indicator',
        'master_indicator_sub',
        'master_indicator_sub_sub',
        'individual_indicator',
        'calculated_indicator',
        'hpm_indicator',
        'separator_indicator',
        # 'tag_gender',
        # 'tag_age',
        # 'tag_nationality',
        # 'tag_disability',
    )
    list_display = (
        'id',
        'ai_indicator',
        'awp_code',
        'name',
        'target',
        'target_sector',
        'units',
        'activity',
        #'sequence',
        'master_indicator',
        'hpm_indicator',
        'has_hpm_note',
        'list_header',
        'category',
        'sequence',
        'is_sector',
        'is_section',
        'support_COVID'
        # 'support_disability',
        # 'values_tags'
    )
    filter_horizontal = (
        'sub_indicators',
        'summation_sub_indicators',
    )
    list_editable = (
        'awp_code',
        'target',
        'target_sector',
        #'sequence',
        'master_indicator',
        'hpm_indicator',
        'has_hpm_note',
        'list_header',
        'category',
        'sequence',
        'is_sector',
        'support_COVID',
        # 'is_section',
        # 'support_disability',
        # 'values_tags'
    )

    formfield_overrides = {
        JSONField: {'widget': JSONEditorWidget(attrs={'initial': 'parsed'})},
        # models.ManyToManyField: {'widget': FilteredSelectMultiple('indicator', is_stacked=False)}
    }

    fieldsets = [
        ('Basic infos', {
            'classes': ('suit-tab', 'suit-tab-general',),
            'fields': [
                'ai_indicator',
                'awp_code',
                'name',
                'label',
                'hpm_label',
                'description',
                'explication',
                'activity',
                'list_header',
                'type',
                'reporting_level',
                'target',
                'target_sector',
                'target_sub_total',
                'units',
                'category',
                'status',
                'status_color',
                'none_ai_indicator',
                'funded_by',
                'sequence',
                'is_sector',
                'is_section',
                'support_disability',
                'support_COVID',
                'is_cumulative'
            ]
        }),
        ('Tags', {
            'classes': ('suit-tab', 'suit-tab-general',),
            'fields': [
                'tag_age',
                'tag_gender',
                'tag_nationality',
                'tag_disability',
                'tag_programme',
                'tag_focus',
                'hpm_indicator',
                'comment',
                'target_hpm',
                'has_hpm_note',
                'hpm_additional_cumulative',
                'hpm_global_indicator'
            ]
        }),
        ('Sub indicators', {
            'classes': ('suit-tab', 'suit-tab-general',),
            'fields': [
                'master_indicator',
                'master_indicator_sub',
                'master_indicator_sub_sub',
                'individual_indicator',
                'separator_indicator',
                'calculated_indicator',
                'calculated_percentage',
                'measurement_type',
                'numerator_indicator',
                'denominator_indicator',
                'denominator_multiplication',
                'sub_indicators',
                'summation_sub_indicators',
            ]
        }),
        ('Calculated Values', {
            'classes': ('suit-tab', 'suit-tab-report-values',),
            'fields': [
                'values',
                'values_gov',
                'values_partners',
                'values_partners_gov',
                'cumulative_values',
            ]
        }),
        ('Calculated Values sector', {
            'classes': ('suit-tab', 'suit-tab-report-values-sector',),
            'fields': [
                'values_sector',
                'values_sites_sector',
                'values_partners_sector',
                'values_partners_sites_sector',
                'cumulative_values_sector',
                'values_tags_sector',
            ]
        }),
        ('Calculated HPM Values', {
            'classes': ('suit-tab', 'suit-tab-hpm-values',),
            'fields': [
                'values_hpm',
                'values_tags',
                'cumulative_values_hpm',
            ]
        }),
        ('Calculated Values live', {
            'classes': ('suit-tab', 'suit-tab-live-values',),
            'fields': [
                'values_live',
                'values_gov_live',
                'values_partners_live',
                'values_partners_gov_live',
                'cumulative_values_live',
            ]
        }),
        ('Partner Targets', {
            'classes': ('suit-tab', 'suit-tab-partner-targets',),
            'fields': [
            ]
        }),
    ]

    suit_form_tabs = (
                      ('general', 'Indicator'),
                      ('report-values', 'Report values'),
                      ('report-values-sector', 'Report values sector'),
                      ('hpm-values', 'HPM values'),
                      ('live-values', 'Live values'),
                      ('partner-targets', 'Partner Targets'),
                    )


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
        'location_adminlevel_governorate',
        'form',
        'form_category',
        'funded_by',
        'year',
        'month_name',
        'master_indicator',
        'partner_ai',
    )
    suit_list_filter_horizontal = (
        'start_date',
        'database',
        'partner_label',
        'location_adminlevel_governorate',
        'form',
        'form_category',
        'funded_by',
        'year',
        'month_name',
        'partner_ai',
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
        'partner_id'
    )
    fields = (

    )
    exclude = (
        'location_cadastral',
        'location_caza',
        'location_governorate',
    )

    readonly_fields = (
        'ai_indicator',
        'partner_ai',
    )
    date_hierarchy = 'start_date'

    # def get_readonly_fields(self, request, obj=None):
    #     if request.user.is_superuser:
    #         return list(set(
    #             [field.name for field in self.opts.local_fields] +
    #             [field.name for field in self.opts.local_many_to_many]
    #         ))
    #
    #     return self.readonly_fields


class LiveActivityReportAdmin(RelatedFieldAdmin):
    # resources = ActivityReportResource
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
        'is_sector',
        'display',
        'hpm_sequence'
    )
    list_editable = (
        'is_sector',
        'hpm_sequence'
    )
    readonly_fields = (
        'description',
        'country_name',
        'ai_country_id'
    )
    actions = [
        'import_partners',
        're_formatting_json',
        'import_basic_data',
        'update_basic_data',
        'import_only_new',
        # 'import_data',
        # 'import_reports',
        'import_reports_forced',
        'link_indicators_data',
        'calculate_indicators_values',
        'calculate_indicators_cumulative_results',
        'calculate_indicators_status',
        'reset_indicators_values',
        'update_indicators_report',
        'update_hpm_report',
        'reset_hpm_indicators_values',
        'update_indicators_hpm',
        'calculate_indicators_cumulative_hpm',
        'calculate_indicators_tags_hpm',
        'calculate_indicators_tags',
        'update_partner_data',
        'generate_indicator_tags',
        'calculate_sum_target',
        'update_indicator_list_header',
        'update_indicator_name',
    ]

    fieldsets = [
        (None, {
            'classes': ('suit-tab', 'suit-tab-general',),
            'fields': [
                'ai_id',
                'db_id',
                'name',
                'label',
                'sector_label',
                'hpm_label',
                'hpm_sequence',
                'username',
                'password',
                'section',
                'reporting_year',
                'focal_point',
                'focal_point_sector',
                'mapped_db',
                'is_funded_by_unicef',
                'is_sector',
                'display',
                'description',
                'country_name',
                'ai_country_id',
                'have_partners',
                'have_governorates',
                'have_covid',
                'have_offices',
                'have_internal_reporting',
                # 'dashboard_link',
            ]
        }),
        ('Extraction mapping', {
            'classes': ('suit-tab', 'suit-tab-general',),
            'fields': [
                # 'mapping_extraction1',
                # 'mapping_extraction2',
                # 'mapping_extraction3',
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

    def re_formatting_json(self, request, queryset):
        from .utilities import import_data_v4
        objects = 0
        for db in queryset:
            objects += import_data_v4(db)
            self.message_user(
                request,
                "{} objects created.".format(objects)
            )

    def import_partners(self, request,queryset):
        from .utilities import import_partners
        objects = 0
        for db in queryset:
            objects += import_partners(db)
        self.message_user(
            request,
            "Partners imported successfully"
        )

    def import_basic_data(self, request, queryset):
        objects = 0
        for db in queryset:
            objects += db.import_data()
        self.message_user(
            request,
            "{} objects created.".format(objects)
        )

    import_basic_data.short_description = 'Step 0: Import Indicators basic structure (only once - ask Ali before!!!)'

    def update_basic_data(self, request, queryset):
        objects = 0
        for db in queryset:
            objects += db.import_data(import_new=False, update_only=True)
        self.message_user(
            request,
            "{} objects created.".format(objects)
        )

    update_basic_data.short_description = 'Step 0a: Update Indicators basic data - ' \
                                          'Update only (only once - ask Ali before!!!)'

    def import_only_new(self, request, queryset):
        objects = 0
        for db in queryset:
            objects += db.import_data(import_new=True)
        self.message_user(
            request,
            "{} objects created.".format(objects)
        )

    import_only_new.short_description = 'Step 0b: Import only new Indicators basic data -' \
                                        ' Import new indicators only(only once - ask Ali before!!!)'

    def update_partner_data(self, request, queryset):
        for db in queryset:
            objects = update_partner_data(db)
            self.message_user(
                request,
                "{}-{} ActivityInfo's partners created for database: ".format(objects, db)
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
        for db in queryset:
            r_script_command_line('ai_generate_excel.R', db)
            self.message_user(
                request,
                "Script R executed for database {}".format(db.name)
            )

    def import_reports(self, request, queryset):
        for db in queryset:
            reports = read_data_from_file(db.ai_id)
            self.message_user(
                request,
                "{} Data imported from the file for database {}".format(reports, db.name)
            )

    def import_reports_forced(self, request, queryset):
        for db in queryset:
            reports = import_data_via_r_script(db)
            self.message_user(
                request,
                "Old data deleted and {} Data imported from the file for database {}".format(reports, db.name)
            )
    import_reports_forced.short_description = 'Step 1: Import Indicator values via R script'

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

    def link_indicators_data(self, request, queryset):
        for db in queryset:
            reports = link_indicators_data(db)
            self.message_user(
                request,
                "{} indicators linked for database {}".format(reports, db.name)
            )
    link_indicators_data.short_description = 'Step 2: Link Indicators info to Indicator values'

    def reset_indicators_values(self, request, queryset):
        for db in queryset:
            reports = reset_indicators_values(db.ai_id)
            self.message_user(
                request,
                "{} indicators pre-calculated values removed and for database {} ".format(reports, db.name)
            )

    def update_hpm_report(self, request, queryset):
        reports = update_hpm_report()
        self.message_user(
            request,
            "Update the HPM report"
        )
    update_hpm_report.short_description = 'Update HPM monthly report (3 in 1)'

    def reset_hpm_indicators_values(self, request, queryset):
        reports = reset_hpm_indicators_values()
        self.message_user(
            request,
            "{} indicators pre-calculated HPM values removed and for database ".format(reports)
        )
    reset_hpm_indicators_values.short_description = 'Step 0: Reset HPM indicators values'

    def update_indicators_hpm(self, request, queryset):
        reports = update_indicators_hpm_data()
        self.message_user(
            request,
            "{} indicators pre-calculated HPM values removed and for database ".format(reports)
        )
    update_indicators_hpm.short_description = 'Step 1: Update HPM indicators values'

    def calculate_indicators_values(self, request, queryset):
        for db in queryset:
            reports = calculate_indicators_values(db)
            self.message_user(
                request,
                "{} indicators values calculated for database {}".format(reports, db.name)
            )
    calculate_indicators_values.short_description = 'Step 3: Reset and calculate monthly report, cumulative and status'

    def calculate_indicators_cumulative_results(self, request, queryset):
        for db in queryset:
            reports = calculate_indicators_cumulative_results_1(db)
            self.message_user(
                request,
                "{} indicators values cumulative calculated for database {}".format(reports, db.name)
            )

    def calculate_indicators_cumulative_hpm(self, request, queryset):
        reports = calculate_indicators_cumulative_hpm()
        self.message_user(
            request,
            "{} indicators values cumulative HPM for database".format(reports)
        )

    calculate_indicators_cumulative_hpm.short_description = 'Step 2: Calculate HPM cumulative values'

    def calculate_indicators_tags_hpm(self, request, queryset):
        for db in queryset:
            reports = calculate_indicators_tags_hpm(db)
            self.message_user(
                request,
                "{} indicators values Tag HPM for database".format(reports)
            )

    calculate_indicators_tags_hpm.short_description = 'Step 3: Calculate HPM indicators percentages'

    def calculate_indicators_tags(self, request, queryset):

        for db in queryset:
            reports = calculate_indicators_tags(db)
            # reports = calculate_indicators_monthly_tags(db)
            self.message_user(
                request,
                "{} indicators values Tag".format(reports)
        )

    def calculate_indicators_status(self, request, queryset):
        reports = 0
        for db in queryset:
            reports = calculate_indicators_status(db)
            self.message_user(
                request,
                "{} indicators status calculated for database {}".format(reports, db.name)
            )

    def update_indicator_name(self, request, queryset):
        reports = 0
        for db in queryset:
            reports = update_indicator_data(ai_db=db, ai_field_name='name', field_name='name')
            self.message_user(
                request,
                "{} indicators status calculated for database {}".format(reports, db.name)
            )

    def update_indicator_list_header(self, request, queryset):
        reports = 0
        for db in queryset:
            reports = update_indicator_data(ai_db=db, ai_field_name='list_header', field_name='listHeader')
            self.message_user(
                request,
                "{} indicators status calculated for database {}".format(reports, db.name)
            )

    formfield_overrides = {
        JSONField: {'widget': JSONEditorWidget(attrs={'initial': 'parsed'})},
    }


class ReportingYearAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'current',
        'database_id',
        'form_id'
    )


class IndicatorTagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'label',
        'type',
        'tag_field',
        'sequence',
    )
    list_editable = (
        'sequence',
    )


@admin.register(AdminLevelEntities)
class AdminLevelEntitiesAdmin(admin.ModelAdmin):
    list_filter = (
        'level',
    )
    search_fields = (
        'code',
        'name',
        'bounds',
    )
    list_display = (
        'code',
        'name',
        'level',
        'parent',
        'bounds',
    )


@admin.register(Locations)
class LocationsAdmin(admin.ModelAdmin):
    list_filter = (
        'type',
    )
    fields = (
        'code',
        'name',
        'type',
        'longitude',
        'latitude',
    )
    search_fields = (
        'id',
        'code',
        'name',
    )
    list_display = (
        'code',
        'name',
        'type',
        'longitude',
        'latitude',
    )


@admin.register(Sites)
class SitesAdmin(admin.ModelAdmin):
    list_filter = (
        'partner',
        'activity',
    )
    fields = (
        'code',
        'name',
        'longitude',
        'latitude',
    )
    search_fields = (
        'code',
        'name',
        'longitude',
        'latitude',
    )
    list_display = (
        'code',
        'name',
        'longitude',
        'latitude',
    )


admin.site.register(AdminLevels)
# admin.site.register(AdminLevelEntities)
admin.site.register(LocationTypes)
# admin.site.register(Locations)
admin.site.register(IndicatorTag, IndicatorTagAdmin)
admin.site.register(ReportingYear, ReportingYearAdmin)
admin.site.register(Database, DatabaseAdmin)
admin.site.register(Partner, PartnerAdmin)
admin.site.register(Activity, ActivityAdmin)
admin.site.register(Indicator, IndicatorAdmin)
admin.site.register(AttributeGroup, AttributeGroupAdmin)
admin.site.register(Attribute, AttributeAdmin)
admin.site.register(ActivityReport, ActivityReportAdmin)
admin.site.register(LiveActivityReport, LiveActivityReportAdmin)

