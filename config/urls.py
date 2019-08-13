# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView
from django.views import defaults as default_views
from rest_framework_nested import routers
from rest_framework_swagger.views import get_swagger_view

from internos.activityinfo.views import IndexView
from internos.etools.views import CommentUpdateViewSet

api = routers.SimpleRouter()
api.register(r'update-partner-comments', CommentUpdateViewSet, base_name='update_partner_comments')
schema_view = get_swagger_view(title='Neuro-DB API')

urlpatterns = [
    # url(r'^$', TemplateView.as_view(template_name='pages/home.html'), name='home'),
    url(r'^$', view=IndexView.as_view(), name='index'),
    url(r'^activityinfo/', include('internos.activityinfo.urls', namespace='activityinfo'), name='activityinfo'),
    url(r'^etools/', include('internos.etools.urls', namespace='etools'), name='etools'),
    url(r'^locations/', include('internos.locations.urls', namespace='locations'), name='locations'),
    url(r'^winterization/', include('internos.winterization.urls', namespace='winterization')),
    url(r'^about/$', TemplateView.as_view(template_name='pages/about.html'), name='about'),

    # Django Admin, use {% url 'admin:index' %}
    url(r'^jet/', include('jet.urls', 'jet')),  # Django JET URLS
    url(r'^jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),  # Django JET dashboard URLS
    url(r'^newsletter/', include('newsletter.urls')),
    url(r'^tellme/', include("tellme.urls")),
    url(settings.ADMIN_URL, admin.site.urls),

    # User management
    url(r'^users/', include('internos.users.urls', namespace='users')),
    url(r'^nested_admin/', include('nested_admin.urls')),
    url(r'^accounts/', include('allauth.urls')),

    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/docs/', schema_view),

    url(r'^api/', include(api.urls)),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        url(r'^400/$', default_views.bad_request, kwargs={'exception': Exception('Bad Request!')}),
        url(r'^403/$', default_views.permission_denied, kwargs={'exception': Exception('Permission Denied')}),
        url(r'^404/$', default_views.page_not_found, kwargs={'exception': Exception('Page not Found')}),
        url(r'^500/$', default_views.server_error),
    ]
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            url(r'^__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
