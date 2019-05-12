from __future__ import unicode_literals

import logging

from django.contrib.gis.db import models
from django.utils.translation import ugettext as _
from model_utils.fields import AutoCreatedField, AutoLastModifiedField
from model_utils.models import TimeStampedModel
from mptt.managers import TreeManager
from mptt.models import MPTTModel, TreeForeignKey

logger = logging.getLogger(__name__)


class LocationType(TimeStampedModel):

    name = models.CharField(max_length=254, unique=True, verbose_name=_('Name'))
    admin_level = models.PositiveSmallIntegerField(null=True, unique=True, verbose_name=_('Admin Level'))

    class Meta:
        ordering = ['name']
        verbose_name = 'Location Type'

    def __str__(self):
        return self.name


class LocationsManager(TreeManager):
    def get_queryset(self):
        return super(LocationsManager, self).get_queryset().filter(is_active=True)\
            .order_by('name').select_related('type')

    def archived_locations(self):
        return super(LocationsManager, self).get_queryset().filter(is_active=False)\
            .order_by('name').select_related('type')

    def all_locations(self):
        return super(LocationsManager, self).get_queryset()\
            .order_by('name').select_related('type')


class Location(MPTTModel):

    name = models.CharField(verbose_name=_("Name"), max_length=254)
    type = models.ForeignKey(
        LocationType, verbose_name=_('Location Type'),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    latitude = models.FloatField(
        verbose_name=_("Latitude"),
        null=True,
        blank=True,
    )
    longitude = models.FloatField(
        verbose_name=_("Longitude"),
        null=True,
        blank=True,
    )
    p_code = models.CharField(
        verbose_name=_("P Code"),
        max_length=32,
        blank=True,
        default='',
    )

    parent = TreeForeignKey(
        'self',
        verbose_name=_("Parent"),
        null=True,
        blank=True,
        related_name='children',
        db_index=True,
        on_delete=models.CASCADE
    )
    geom = models.MultiPolygonField(
        verbose_name=_("Geo Point"),
        null=True,
        blank=True,
    )
    point = models.PointField(verbose_name=_("Point"), null=True, blank=True)
    is_active = models.BooleanField(verbose_name=_("Active"), default=True, blank=True)
    created = AutoCreatedField(_('created'))
    modified = AutoLastModifiedField(_('modified'))

    objects = LocationsManager()

    def __str__(self):
        return self.name.encode('utf-8')

    @property
    def geo_point(self):
        return self.point if self.point else self.geom.point_on_surface if self.geom else ""

    @property
    def point_lat_long(self):
        return "Lat: {}, Long: {}".format(
            self.point.y,
            self.point.x
        )

    class Meta:
        unique_together = ('name', 'type', 'p_code')
        # ordering = ['name']
        app_label = 'locations'
