__author__ = 'achamseddine'

import json
import re
from datetime import datetime
from django.db import models
from model_utils import Choices
from model_utils.models import TimeStampedModel
from django.contrib.postgres.fields import ArrayField, JSONField
# from django_mysql import models as mysql_model

from internos.users.models import Section
from .client import ActivityInfoClient


class Database(models.Model):

    ai_id = models.PositiveIntegerField(
        unique=True,
        verbose_name='ActivityInfo ID'
    )
    name = models.CharField(max_length=254)
    username = models.CharField(max_length=254)
    password = models.CharField(max_length=254)

    # read only fields
    description = models.CharField(max_length=254, null=True)
    country_name = models.CharField(max_length=254, null=True)
    dashboard_link = models.URLField(max_length=1500, null=True)
    ai_country_id = models.PositiveIntegerField(null=True)
    section = models.ForeignKey(
        Section,
        null=True, blank=True
    )

    mapping_extraction1 = JSONField(blank=True, null=True)
    mapping_extraction2 = JSONField(blank=True, null=True)
    mapping_extraction3 = JSONField(blank=True, null=True)
    year = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        choices=Choices(
            ('2017', '2017'),
            ('2018', '2018'),
            ('2019', '2019'),
            ('2020', '2020'),
            ('2021', '2021'),
            ('2022', '2022'),
            ('2023', '2023'),
            ('2024', '2024'),
            ('2025', '2025'),
            ('2026', '2026'),
            ('2027', '2027'),
            ('2028', '2028'),
            ('2029', '2029'),
            ('2030', '2030'),
        )
    )

    def __unicode__(self):
        return self.name

    def import_data(self):
        from .utils import generate_indicator_awp_code
        """
        Import all activities, indicators and partners from
        a ActivityInfo database specified by the AI ID
        """
        client = ActivityInfoClient(self.username, self.password)

        dbs = client.get_databases()
        db_ids = [db['id'] for db in dbs]
        if self.ai_id not in db_ids:
            raise Exception(
                'DB with ID {} not found in ActivityInfo'.format(
                    self.ai_id
                ))

        db_info = client.get_database(self.ai_id)
        self.name = db_info['name']
        self.description = db_info['description']
        self.ai_country_id = db_info['country']['id']
        self.country_name = db_info['country']['name']
        self.save()

        objects = 0
        try:
            for partner in db_info['partners']:
                try:
                    ai_partner = Partner.objects.get(ai_id=partner['id'])
                except Partner.DoesNotExist:
                    ai_partner = Partner(ai_id=partner['id'])
                    objects += 1
                ai_partner.name = partner['name']
                ai_partner.full_name = partner['fullName']
                ai_partner.database = self
                ai_partner.save()

            for activity in db_info['activities']:
                try:
                    ai_activity = Activity.objects.get(ai_id=activity['id'])
                except Activity.DoesNotExist:
                    ai_activity = Activity(ai_id=activity['id'])
                    objects += 1
                ai_activity.name = activity['name']
                ai_activity.location_type = activity['locationType']['name']
                ai_activity.database = self
                ai_activity.save()

                for indicator in activity['indicators']:
                    try:
                        ai_indicator = Indicator.objects.get(ai_id=indicator['id'])
                    except Indicator.DoesNotExist:
                        ai_indicator = Indicator(ai_id=indicator['id'])
                        objects += 1
                    ai_indicator.name = indicator['name']
                    ai_indicator.awp_code = generate_indicator_awp_code(indicator['name'])

                    ai_indicator.units = indicator['units'] if indicator['units'] else '---'
                    ai_indicator.category = indicator['category']
                    ai_indicator.activity = ai_activity
                    ai_indicator.save()

                for attribute_group in activity['attributeGroups']:
                    try:
                        ai_attribute_group = AttributeGroup.objects.get(ai_id=attribute_group['id'])
                    except AttributeGroup.DoesNotExist:
                        ai_attribute_group = AttributeGroup(ai_id=attribute_group['id'])
                        objects += 1
                    ai_attribute_group.name = attribute_group['name']
                    ai_attribute_group.multiple_allowed = attribute_group['multipleAllowed']
                    ai_attribute_group.mandatory = attribute_group['mandatory']
                    ai_attribute_group.activity = ai_activity
                    ai_attribute_group.save()

                    for attribute in attribute_group['attributes']:
                        try:
                            ai_attribute = Attribute.objects.get(ai_id=attribute['id'])
                        except Attribute.DoesNotExist:
                            ai_attribute = Attribute(ai_id=attribute['id'])
                            objects += 1
                        ai_attribute.name = attribute['name']
                        ai_attribute.attribute_group = ai_attribute_group
                        ai_attribute.save()

        except Exception as e:
            raise e

        return objects

    def import_reports(self):

        client = ActivityInfoClient(self.username, self.password)

        reports = 0

        # for each selected indicator get the related AI indicators (one-to-many)
        for ai_indicator in Indicator.objects.filter(activity__database__ai_id=self.ai_id):
            attribute_group = ai_indicator.activity.attributegroup_set.all()
            try:
                funded_by = attribute_group.get(name__contains='Funded by')
            except AttributeGroup.DoesNotExist:
                continue

            # query AI for matching site records for partner, activity, indicator
            sites = client.get_sites(
                activity=ai_indicator.activity.ai_id,
                indicator=ai_indicator.ai_id,
                attribute=funded_by.attribute_set.get(name='UNICEF').ai_id,
            )

            # for those marching sites, create partner report instances
            for site in sites:
                if not 'monthlyReports' in site:
                    continue
                for month, indicators in site['monthlyReports'].items():
                    for indicator in indicators:
                        if indicator['indicatorId'] == ai_indicator.ai_id and indicator['value']:
                            print(indicator['value'])
            #                 report, created = PartnerReport.objects.get_or_create(
            #                     ai_partner=progress.pca.partner.activity_info_partner,
            #                     ai_indicator=ai_indicator,
            #                     location=site['location']['name'],
            #                     month=datetime.strptime(month+'-15', '%Y-%m-%d'),
            #                     indicator_value=indicator['value']
            #                 )
            #                 if created:
            #                     reports += 1
        return reports


class Partner(models.Model):

    ai_id = models.PositiveIntegerField(unique=True)
    database = models.ForeignKey(Database)
    name = models.CharField(max_length=254)
    full_name = models.CharField(max_length=254, null=True)

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name


class Activity(models.Model):

    ai_id = models.PositiveIntegerField(unique=True)
    database = models.ForeignKey(Database)
    name = models.CharField(max_length=254)
    location_type = models.CharField(max_length=254)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'activities'


class IndicatorCategory(models.Model):

    name = models.CharField(max_length=254)
    reporting_level = models.CharField(max_length=254, blank=True, null=True)
    awp_code = models.CharField(max_length=254, blank=True, null=True)
    target = models.PositiveIntegerField(default=0)
    cumulative_results = models.PositiveIntegerField(default=0)
    units = models.CharField(max_length=254, blank=True, null=True)
    status = models.CharField(max_length=254, blank=True, null=True)

    def __unicode__(self):
        return self.name


class Indicator(models.Model):

    ai_id = models.PositiveIntegerField(blank=True, null=True)
    activity = models.ForeignKey(Activity)
    name = models.CharField(max_length=254)
    indicator_details = models.CharField(max_length=250, blank=True, null=True)
    indicator_master = models.CharField(max_length=250, blank=True, null=True)
    indicator_info = models.CharField(max_length=250, blank=True, null=True)
    reporting_level = models.CharField(max_length=254, blank=True, null=True)
    awp_code = models.CharField(max_length=254, blank=True, null=True)
    target = models.PositiveIntegerField(default=0)
    target_sub_total = models.PositiveIntegerField(default=0)
    cumulative_results = models.PositiveIntegerField(default=0)
    units = models.CharField(max_length=254, blank=True, null=True)
    category = models.CharField(max_length=254, blank=True, null=True)
    status = models.CharField(max_length=254, blank=True, null=True)
    master_indicator = models.BooleanField(default=False)
    master_indicator_sub = models.BooleanField(default=False)
    sub_indicators = models.ManyToManyField('self', blank=True, related_name='sub_indicators')
    summation_sub_indicators = models.ManyToManyField('self', blank=True, related_name='summation_sub_indicators')
    values = JSONField(blank=True, null=True)
    values_gov = JSONField(blank=True, null=True)
    values_partners = JSONField(blank=True, null=True)

    def __unicode__(self):
        return self.name

    @property
    def ai_indicator(self):
        return '{0:0>10}'.format(self.ai_id)

    class Meta:
        ordering = ['id']


class AttributeGroup(models.Model):

    activity = models.ForeignKey(Activity)
    ai_id = models.PositiveIntegerField(unique=True)
    name = models.CharField(max_length=254)
    multiple_allowed = models.BooleanField()
    mandatory = models.BooleanField()

    def __unicode__(self):
        return self.name


class Attribute(models.Model):

    attribute_group = models.ForeignKey(AttributeGroup)
    ai_id = models.PositiveIntegerField(unique=True)
    name = models.CharField(max_length=254)


class ActivityReport(TimeStampedModel):
    end_date = models.CharField(max_length=250, blank=True, null=True)
    form = models.CharField(max_length=250, blank=True, null=True)
    form_category = models.CharField(max_length=250, blank=True, null=True)
    ai_indicator = models.ForeignKey(Indicator, blank=True, null=True)
    indicator_category = models.CharField(max_length=250, blank=True, null=True)
    indicator_id = models.CharField(max_length=250, blank=True, null=True)
    indicator_name = models.CharField(max_length=250, blank=True, null=True)
    indicator_details = models.CharField(max_length=250, blank=True, null=True)
    indicator_master = models.CharField(max_length=250, blank=True, null=True)
    indicator_info = models.CharField(max_length=250, blank=True, null=True)
    indicator_units = models.CharField(max_length=250, blank=True, null=True)
    indicator_value = models.PositiveIntegerField(blank=True, null=True)
    indicator_sub_value = models.CharField(max_length=250, blank=True, null=True)
    indicator_awp_code = models.CharField(max_length=254, blank=True, null=True)
    location_adminlevel_cadastral_area = models.CharField(max_length=250, blank=True, null=True)
    location_adminlevel_cadastral_area_code = models.CharField(max_length=250, blank=True, null=True)
    location_adminlevel_caza = models.CharField(max_length=250, blank=True, null=True)
    location_adminlevel_caza_code = models.CharField(max_length=250, blank=True, null=True)
    location_adminlevel_governorate = models.CharField(max_length=250, blank=True, null=True)
    location_adminlevel_governorate_code = models.CharField(max_length=250, blank=True, null=True)
    governorate = models.CharField(max_length=250, blank=True, null=True)
    location_alternate_name = models.CharField(max_length=250, blank=True, null=True)
    location_latitude = models.CharField(max_length=250, blank=True, null=True)
    location_longitude = models.CharField(max_length=250, blank=True, null=True)
    location_name = models.CharField(max_length=250, blank=True, null=True)
    partner_description = models.CharField(max_length=250, blank=True, null=True)
    partner_id = models.CharField(max_length=250, blank=True, null=True)
    partner_label = models.CharField(max_length=250, blank=True, null=True)
    project_description = models.CharField(max_length=250, blank=True, null=True)
    project_label = models.CharField(max_length=250, blank=True, null=True)
    lcrp_appeal = models.CharField(max_length=250, blank=True, null=True)
    funded_by = models.CharField(max_length=250, blank=True, null=True)
    report_id = models.CharField(max_length=250, blank=True, null=True)
    site_id = models.CharField(max_length=250, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    outreach_platform = models.CharField(max_length=250, blank=True, null=True)
    database_id = models.CharField(max_length=250, blank=True, null=True)
    database = models.CharField(max_length=250, blank=True, null=True)
    month = models.CharField(max_length=250, blank=True, null=True)
    day = models.CharField(max_length=250, blank=True, null=True)
    month_name = models.CharField(max_length=250, blank=True, null=True)
    year = models.CharField(max_length=250, blank=True, null=True)
    master_indicator = models.BooleanField(default=False)
    master_indicator_sub = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
