from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [

    url(
        regex=r'^partner-profile/$',
        view=views.PartnerProfileView.as_view(),
        name='partner_profile'
    ),
]
