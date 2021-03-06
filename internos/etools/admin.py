
from django.contrib import admin
from django.contrib.postgres.fields import JSONField, ArrayField
from django_json_widget.widgets import JSONEditorWidget
from import_export import resources, fields
from import_export import fields
from import_export.admin import ImportExportModelAdmin

from .models import (
    PartnerOrganization,
    Agreement,
    PCA,
    PartnerStaffMember,
    Travel,
    TravelActivity,
    ItineraryItem,
    Engagement,
    ActionPoint,
    Category
)


class PartnerStaffMemberInline(admin.TabularInline):
    model = PartnerStaffMember
    max_num = 99
    min_num = 0
    extra = 1
    verbose_name = 'Partner staff member'
    verbose_name_plural = 'Partner staff members'

    fields = (
        'title',
        'first_name',
        'last_name',
        'email',
        'phone',
        'active',
    )


class PartnerOrganizationResource(resources.ModelResource):
    class Meta:
        model = PartnerOrganization
        fields = (
            'id',
            'vendor_number',
            'name',
            'short_name',
            'partner_type',
            'cso_type',
            'rating',
            'shared_partner',
            'email',
            'phone_number',
        )
        export_order = fields


class PartnerOrganizationAdmin(ImportExportModelAdmin):
    resource_class = PartnerOrganizationResource

    readonly_fields = (
        'vendor_number',
        'name',
        'short_name',
        'partner_type',
        'cso_type',
        'rating',
        'shared_partner',
        'email',
        'phone_number',
    )

    fields = (
        'vendor_number',
        'name',
        'short_name',
        'partner_type',
        'cso_type',
        'rating',
        'shared_partner',
        'email',
        'phone_number',
        'comments',
    )
    search_fields = (
        'name',
    )

    inlines = [PartnerStaffMemberInline, ]


class AgreementResource(resources.ModelResource):
    class Meta:
        model = Agreement
        fields = (
            'id',
            'partner_name',
            'agreement_type',
            'agreement_number',
            'start',
            'end',
            'signed_by_unicef_date',
            'signed_by_partner_date',
        )
        export_order = fields


class AgreementAdmin(ImportExportModelAdmin):
    resource_class = AgreementResource


class PCAResource(resources.ModelResource):
    class Meta:
        model = PCA
        fields = (
            'id',
            'number',
            'document_type',
            'partner_name',
            'status',
            'title',
            'start',
            'end',
            'country_programme',
            'signed_by_unicef_date',
            'signed_by_partner_date',
        )
        export_order = fields


class PCAAdmin(ImportExportModelAdmin):
    resource_class = PCAResource

    list_display = (
        'number',
        'title',
        'partner',
        'agreement',
        'document_type',
        'country_programme',
        'location_p_codes',
        'section_names',
        'status',
        'start',
        'end',
    )
    suit_list_filter_horizontal = (
        'status',
        'section_names',
        'partner',
        'document_type',
        'country_programme',
    )

    list_filter = (
        'status',
        'section_names',
        'partner',
        'document_type',
        'country_programme',
    )

    search_fields = (
        'number',
        'partner_name',
    )
    filter_horizontal = (
        'activities',
    )
    fields = (
        'activities',
    )


class PartnerStaffMemberResource(resources.ModelResource):
    class Meta:
        model = PartnerStaffMember
        fields = (
        )
        export_order = fields


class PartnerStaffMemberAdmin(ImportExportModelAdmin):
    resource_class = PartnerStaffMemberResource
    fields = (
        'title',
        'first_name',
        'last_name',
        'email',
        'phone',
        'active',
    )
    list_display = (
        'partner',
        'title',
        'first_name',
        'last_name',
        'email',
        'phone',
        'active',
    )
    list_filter = (
        'partner',
        'active',
    )
    search_fields = (
        'partner__name',
        'first_name',
        'last_name',
        'email',
        'phone',
    )


@admin.register(Engagement)
class EngagementAdmin(admin.ModelAdmin):
    list_display = [
        '__str__', 'status', 'partner', 'date_of_field_visit',
        'engagement_type', 'start_date', 'end_date',
    ]
    list_filter = [
        'status', 'start_date', 'end_date', 'status', 'engagement_type',
    ]
    readonly_fields = ('status', 'partner',)
    search_fields = 'partner__name', 'agreement__auditor_firm__name',
    fields = (
        'unique_id',
        'engagement_type',
        'status',
        'start_date',
        'end_date',
        'partner',
        'partner_contacted_at',
        'total_value',
        'exchange_rate',
        'date_of_field_visit',
        'date_of_draft_report_to_ip',
        'date_of_comments_by_ip',
        'date_of_draft_report_to_unicef',
        'date_of_comments_by_unicef',
        'date_of_report_submit',
        'date_of_final_report',
        'date_of_cancel',
        'cancel_comment',
        'internal_controls',
        'final_report',
        'audited_expenditure',
        'financial_findings',
        'audit_opinion',
        'description',
        'finding',
        'pending_unsupported_amount',
        'findings',
    )

    formfield_overrides = {
        JSONField: {'widget': JSONEditorWidget(attrs={'initial': 'parsed'})},
        # models.ManyToManyField: {'widget': FilteredSelectMultiple('indicator', is_stacked=False)}
    }


@admin.register(Travel)
class TravelAdmin(admin.ModelAdmin):
    list_filter = (
        'status',
        'travel_type',
        'traveler',
        'section',
        'start_date',
    )
    search_fields = (
        'reference_number',
    )
    list_display = (
        'reference_number',
        'traveler',
        'status',
        'start_date',
        'end_date',
        'section'
    )
    readonly_fields = (
        'status',
    )
    raw_id_fields = (
        'traveler',
        'supervisor'
    )
    date_hierarchy = 'start_date'


@admin.register(TravelActivity)
class TravelActivityAdmin(admin.ModelAdmin):
    list_filter = (
        'travel_type',
        'partner',
        'date',
    )
    search_fields = (
        'primary_traveler__first_name',
        'primary_traveler__last_name',
    )
    list_display = (
        'travel',
        # 'primary_traveler',
        'travel_type',
        'date'
    )
    raw_id_fields = (
        'primary_traveler',
    )
    date_hierarchy = 'date'


@admin.register(ItineraryItem)
class ItineraryItemAdmin(admin.ModelAdmin):
    list_filter = (
        'travel',
        'departure_date',
        'arrival_date',
        'origin',
        'destination'
    )
    search_fields = (
        'travel__reference_number',
    )
    list_display = (
        'travel',
        'departure_date',
        'arrival_date',
        'origin',
        'destination'
    )


class CategoryResource(resources.ModelResource):

    class Meta:
        model = Category
        fields = (
            'id',
            'module',
            'description',
        )
        export_order = fields


class CategoryAdmin(ImportExportModelAdmin):
    resource_class = CategoryResource
    list_display = ('module', 'description')
    list_filter = ('module', )
    search_fields = ('description', )


# SnapshotModelAdmin
class ActionPointAdmin(admin.ModelAdmin):
    list_display = (
        'author_name',
        'assigned_to_name',
        'status',
        'date_of_completion',
        'related_module',
        'description',
        'engagement'
    )
    list_filter = ('status', 'related_module', )
    search_fields = ('author_name', 'assigned_to_name')
    readonly_fields = ('status', )
    raw_id_fields = ('section', 'office', 'location', 'partner', 'intervention',
                     'travel_activity', 'engagement', 'author', 'assigned_by', 'assigned_to')


admin.site.register(ActionPoint, ActionPointAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(PartnerOrganization, PartnerOrganizationAdmin)
admin.site.register(Agreement, AgreementAdmin)
admin.site.register(PCA, PCAAdmin)
# admin.site.register(Travel)
# admin.site.register(Engagement)
admin.site.register(PartnerStaffMember, PartnerStaffMemberAdmin)
