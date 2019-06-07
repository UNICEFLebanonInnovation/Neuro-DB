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
        regex=r'^report-partner/$',
        view=views.ReportPartnerView.as_view(),
        name='report_partner'
    ),
    url(
        regex=r'^report-map/$',
        view=views.ReportMapView.as_view(),
        name='report_map'
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

]
