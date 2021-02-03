from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [

    url(
        regex=r'^Economic-Dashboard/2020/$',
        view=views.EconomicDashboardView.as_view(),
        name='economic_dashboard'
    ),
    url(
        regex=r'^Population-Figures-in-Lebanon/2020/$',
        view=views.PopulationFiguresView.as_view(),
        name='population_figures'
    ),
    url(
        regex=r'^Child-Protection-Working-Group-Real-time-monitoring/2020/$',
        view=views.ChildProtectionView.as_view(),
        name='child_protection'
    ),
    url(
        regex=r'^Data-Sets/$',
        view=views.DataSetsView.as_view(),
        name='data_sets'
    ),
    url(
        r'^Maps/$',
        views.MapsView.as_view(),
        name='maps'
    ),

    url(
        r'^Researches/$',
        views.ResearchesView.as_view(),
        name='researches'
    ),
]
