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
        regex=r'^activityinfo/dashboard/$',
        view=views.DashboardView.as_view(),
        name='dashboard'
    ),
    url(
        regex=r'^activityinfo-export/$',
        view=views.ExportViewSet.as_view(),
        name='export'
    ),
    url(
        regex=r'^activityinfo/report/$',
        view=views.ReportView.as_view(),
        name='report'
    ),
    url(
        regex=r'^activityinfo/live-report/$',
        view=views.LiveReportView.as_view(),
        name='live_report'
    ),
]
