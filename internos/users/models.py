# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.contrib.auth.models import AbstractUser
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _


class Section(models.Model):
    name = models.CharField(max_length=256)
    logo = models.CharField(max_length=256, null=True, blank=True)
    code = models.CharField(max_length=10, null=True, blank=True)
    color = models.CharField(max_length=50, null=True, blank=True)
    have_hpm_indicator = models.BooleanField(default=False)
    powerbi_url = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class Office(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class User(AbstractUser):

    # First Name and Last Name do not cover name patterns
    # around the globe.
    name = models.CharField(_('Name of User'), blank=True, max_length=255)
    skype_account = models.CharField(blank=True, max_length=255)
    section = models.ForeignKey(
        Section,
        null=True, blank=True
    )
    backup_user = models.ForeignKey(
        'self',
        null=True, blank=True
    )

    def __str__(self):
        return '{} {}'.format(self.first_name, self.last_name)

    def get_absolute_url(self):
        return reverse('users:detail', kwargs={'username': self.username})
