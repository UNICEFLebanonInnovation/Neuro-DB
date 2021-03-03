from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [

    url(
        regex=r'^partner-profile/$',
        view=views.PartnerProfileView.as_view(),
        name='partner_profile'
    ),
    url(
        regex=r'^partnership/$',
        view=views.PartnershipView.as_view(),
        name='partnership'
    ),
    url(
        regex=r'^donor-mapping/$',
        view=views.DonorMappingView.as_view(),
        name='donor_mapping'
    ),
    url(
        regex=r'^donor-interventions/$',
        view=views.DonorInterventionsView.as_view(),
        name='donor_interventions'
    ),
    url(
        regex=r'^donor-programme-results/$',
        view=views.DonorProgrammeResultsView.as_view(),
        name='donor_programme_results'
    ),
    url(
        regex=r'^donor-funding/$',
        view=views.DonorFundingView.as_view(),
        name='donor_funding'
    ),
    url(
        'load-donor-locations/$',
        views.load_donor_locations,
        name='load_donor_locations'
    ),
    url(
        regex=r'^partner-profile-map/$',
        view=views.PartnerProfileMapView.as_view(),
        name='partner_profile_map'
    ),
    url(
        regex=r'^interventions/$',
        view=views.InterventionsView.as_view(),
        name='interventions'
    ),
    url(
        regex=r'^programmatic-visits-monitoring/$',
        view=views.TripsMonitoringView.as_view(),
        name='programmatic_visits_monitoring'
    ),
    url(
        regex=r'^HACT/$',
        view=views.HACTView.as_view(),
        name='hact'
    ),
    url(
        regex=r'^interventions-export/$',
        view=views.InterventionExportViewSet.as_view(),
        name='interventions_export'
    ),
]
