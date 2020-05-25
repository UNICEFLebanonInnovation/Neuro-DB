from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [

    url(
        regex=r'^$',
        view=views.IndexView.as_view(),
        name='index'
    ),
    url(
        regex=r'^dashboard/$',
        view=views.DashboardView.as_view(),
        name='dashboard'
    ),
    url(
        regex=r'^HPM/$',
        view=views.HPMView.as_view(),
        name='hpm'
    ),
    url(
        regex=r'^export/$',
        view=views.ExportViewSet.as_view(),
        name='export'
    ),
    url(
        regex=r'^report/$',
        view=views.ReportView.as_view(),
        name='report'
    ),
    url(
        regex=r'^report-internal/$',
        view=views.ReportInternalView.as_view(),
        name='report_internal'
    ),
    url(
        regex=r'^report-internal-form/$',
        view=views.ReportInternalFormView.as_view(),
        name='report_internal_form'
    ),
    url(
        regex=r'^report-crisis/$',
        view=views.ReportCrisisView.as_view(),
        name='report_crisis'
    ),
    url(
        regex=r'^report-crisis-live/$',
        view=views.ReportLiveCrisis.as_view(),
        name='report_crisis_live'
    ),
    url(
        regex=r'^report-crisis-tags/$',
        view=views.ReportCrisisTags.as_view(),
        name='report_crisis_tags'
    ),
    url(
        regex=r'^report-partner/$',
        view=views.ReportPartnerView.as_view(),
        name='report_partner'
    ),
    url(
        regex=r'^report-partner-sector/$',
        view=views.ReportPartnerSectorView.as_view(),
        name='report_partner_sector'
    ),
    url(
        regex=r'^report-map/$',
        view=views.ReportMapView.as_view(),
        name='report_map'
    ),
    url(
        regex=r'^report-map-sector/$',
        view=views.ReportMapSectorView.as_view(),
        name='report_map_sector'
    ),
    url(
        regex=r'^report-disability/$',
        view=views.ReportDisabilityView.as_view(),
        name='report_disability'
    ),
    url(
        regex=r'^report-sector/$',
        view=views.ReportSectorView.as_view(),
        name='report_sector'
    ),
    url(
        regex=r'^report-tags/$',
        view=views.ReportTagView.as_view(),
        name='report_tags'
    ),
    url(
        regex=r'^live-report/$',
        view=views.LiveReportView.as_view(),
        name='live_report'
    ),
    url(
        regex=r'^HPM-report/$',
        view=views.HPMExportViewSet.as_view(),
        name='hpm_report'
    ),
    url(
        regex='ajax/load-sections/',
        view=views.load_sections,
        name='ajax_load_sections'
    ),
    url(
        regex='ajax/load-govs/',
        view=views.load_governorates,
        name='ajax_load_govs'
    ),
    url(
        regex='ajax/load-months/',
        view=views.load_months,
        name='ajax_load_months'
    ),
    url(
        regex='ajax/load-partners/',
        view=views.load_partners,
        name='ajax_load_partners'
    ),

]
