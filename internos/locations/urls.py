from django.conf.urls import include, url
from rest_framework import routers

from . import views

app_name = 'locations'

api = routers.SimpleRouter()

api.register(r'locations', views.LocationsViewSet, base_name='locations')
api.register(r'locations-light', views.LocationsLightViewSet, base_name='locations-light')

urlpatterns = [
    url(r'', include(api.urls)),
    url(
        r'^locations/pcode/(?P<p_code>\w+)/$', views.LocationsViewSet.as_view({'get': 'retrieve'}),
        name='locations_detail_pcode'
    ),
    url(r'^autocomplete/$', views.LocationQuerySetView.as_view(), name='locations_autocomplete'),
    url(
        regex=r'^site-profile/$',
        view=views.SiteProfileView.as_view(),
        name='site_profile'
    ),
]
