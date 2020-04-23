from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [

    url(
        regex=r'^economic-dashboard/2020/$',
        view=views.EconomicDashboardView.as_view(),
        name='economic_dashboard'
    )
]
