__author__ = 'achamseddine'

import json
import re
from datetime import datetime
from django.db import models
from django.conf import settings
from model_utils import Choices
from model_utils.models import TimeStampedModel
from django.contrib.postgres.fields import ArrayField, JSONField
# from django_mysql import models as mysql_model

from internos.users.models import Section
from internos.etools.models import PartnerOrganization
from .client import ActivityInfoClient


class ReportingYear(models.Model):
    name = models.CharField(max_length=254)
    current = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name


class Database(models.Model):

    ai_id = models.PositiveIntegerField(
        unique=True,
        verbose_name='ActivityInfo ID'
    )
    name = models.CharField(max_length=254)
    label = models.CharField(max_length=254, null=True, blank=True)
    username = models.CharField(max_length=254)
    password = models.CharField(max_length=254)
    focal_point = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True, null=True,
        related_name='+',
    )

    # read only fields
    description = models.CharField(max_length=1500, null=True)
    country_name = models.CharField(max_length=254, null=True)
    dashboard_link = models.URLField(max_length=1500, null=True, blank=True)
    ai_country_id = models.PositiveIntegerField(null=True)
    section = models.ForeignKey(
        Section,
        null=True, blank=True
    )
    mapped_db = models.BooleanField(default=True)
    mapping_extraction1 = JSONField(blank=True, null=True)
    mapping_extraction2 = JSONField(blank=True, null=True)
    mapping_extraction3 = JSONField(blank=True, null=True)
    is_funded_by_unicef = models.BooleanField(default=False)
    reporting_year = models.ForeignKey(
        ReportingYear,
        blank=True,
        null=True
    )
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

    def create_master_indicator(self, indicator, ai_indicator):
        if not 'description' in indicator or not indicator['description'] or '------' in indicator['name']:
            return False

        try:
            master_indicator = Indicator.objects.get(name=indicator['description'], master_indicator=True)
        except Indicator.DoesNotExist:
            master_indicator = Indicator(name=indicator['description'], master_indicator=True)

        master_indicator.activity = ai_indicator.activity
        master_indicator.save()
        master_indicator.sub_indicators.add(ai_indicator)

    def import_data(self, import_new=True, update_only=False):
        from .utils import get_awp_code, get_label
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
            partners = []
            if 'databasePartners' in db_info:
                partners = db_info['databasePartners']
            else:
                partners = db_info['partners']
            for partner in partners:
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
                    new_instance = False
                    try:
                        ai_indicator = Indicator.objects.get(ai_id=indicator['id'])
                    except Indicator.DoesNotExist:
                        if not import_new:
                            continue
                        ai_indicator = Indicator(ai_id=indicator['id'])
                        new_instance = True
                        objects += 1

                    if update_only:
                        ai_indicator.name = indicator['name']
                        ai_indicator.label = get_label(indicator)

                    if new_instance:
                        ai_indicator.awp_code = get_awp_code(indicator['name'])
                        ai_indicator.description = indicator['description'] if 'description' in indicator else ''
                        ai_indicator.name = indicator['name']
                        ai_indicator.label = get_label(indicator)

                    ai_indicator.list_header = indicator['listHeader'] if 'listHeader' in indicator else ''
                    ai_indicator.type = indicator['type'] if 'type' in indicator else ''

                    ai_indicator.units = indicator['units'] if indicator['units'] else '---'
                    ai_indicator.category = indicator['category']
                    ai_indicator.activity = ai_activity
                    ai_indicator.save()

                    if new_instance and self.mapped_db:
                        self.create_master_indicator(indicator, ai_indicator)

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
    number = models.CharField(max_length=254, blank=True, null=True)
    database = models.ForeignKey(Database)
    name = models.CharField(max_length=254)
    full_name = models.CharField(max_length=254, null=True)
    partner_etools = models.ForeignKey(PartnerOrganization, blank=True, null=True, related_name='+')

    @property
    def ai_number(self):
        if len(str(self.ai_id)) == 10:
            return self.ai_id
        return 'p{0:0>10}'.format(str(self.ai_id))

    @property
    def detailed_info(self):
        partner_etools = self.partner_etools
        return {
            'etl_id': partner_etools.etl_id,
            'name': partner_etools.name,
            'type': partner_etools.partner_type,
            'rating': partner_etools.rating,
            'interventions': partner_etools.interventions_details,
            'programmatic_visits': partner_etools.programmatic_visits,
            'audits': partner_etools.audits,
            'micro_assessments': partner_etools.micro_assessments,
            'spot_checks': partner_etools.spot_checks,
            'special_audits': partner_etools.special_audits,
        }

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name


class Activity(models.Model):

    ai_id = models.PositiveIntegerField(unique=True)
    database = models.ForeignKey(Database)
    none_ai_database = models.ForeignKey(Database, blank=True, null=True, related_name='+')
    name = models.CharField(max_length=1500)
    location_type = models.CharField(max_length=254)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'activities'


class IndicatorTag(models.Model):

    name = models.CharField(max_length=254)
    label = models.CharField(max_length=254, blank=True, null=True)
    type = models.CharField(max_length=254, blank=True, null=True)
    tag_field = models.CharField(max_length=254, blank=True, null=True)

    def __unicode__(self):
        return self.name


class IndicatorCategory(models.Model):

    name = models.CharField(max_length=1500)
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
    name = models.CharField(max_length=5000)
    label = models.CharField(max_length=5000, blank=True, null=True)
    description = models.CharField(max_length=1500, blank=True, null=True)
    explication = models.TextField(blank=True, null=True)
    list_header = models.CharField(max_length=250, blank=True, null=True)
    type = models.CharField(max_length=250, blank=True, null=True)
    indicator_details = models.CharField(max_length=250, blank=True, null=True)
    indicator_master = models.CharField(max_length=250, blank=True, null=True)
    indicator_info = models.CharField(max_length=250, blank=True, null=True)
    ai_indicator = models.CharField(max_length=250, blank=True, null=True)
    reporting_level = models.CharField(max_length=254, blank=True, null=True)
    awp_code = models.CharField(max_length=1500, blank=True, null=True, verbose_name='RWP')
    target = models.PositiveIntegerField(default=0)
    target_sector = models.PositiveIntegerField(default=0)
    target_sub_total = models.PositiveIntegerField(default=0)
    cumulative_results = models.PositiveIntegerField(default=0)
    units = models.CharField(max_length=254, blank=True, null=True)
    category = models.CharField(max_length=254, blank=True, null=True)
    status = models.CharField(max_length=254, blank=True, null=True)
    status_color = models.CharField(max_length=254, blank=True, null=True)
    master_indicator = models.BooleanField(default=False, verbose_name='Master indicator level 1')
    master_indicator_sub = models.BooleanField(default=False, verbose_name='Master indicator level 2')
    master_indicator_sub_sub = models.BooleanField(default=False, verbose_name='Master indicator level 3')
    individual_indicator = models.BooleanField(default=False)
    calculated_indicator = models.BooleanField(default=False)
    calculated_percentage = models.PositiveIntegerField(default=0)
    sub_indicators = models.ManyToManyField('self', blank=True, related_name='top_indicator')
    summation_sub_indicators = models.ManyToManyField('self', blank=True, related_name='summation_top_indicator')
    denominator_indicator = models.ForeignKey('self', blank=True, null=True, related_name='+')
    numerator_indicator = models.ForeignKey('self', blank=True, null=True, related_name='+')
    denominator_summation = models.ManyToManyField('self', blank=True, related_name='+')
    numerator_summation = models.ManyToManyField('self', blank=True, related_name='+')
    main_master_indicator = models.ForeignKey('self', blank=True, null=True, related_name='+')
    values = JSONField(blank=True, null=True)
    values_hpm = JSONField(blank=True, null=True, default={})
    values_tags = JSONField(blank=True, null=True, default={})
    values_gov = JSONField(blank=True, null=True)
    values_partners = JSONField(blank=True, null=True)
    values_partners_gov = JSONField(blank=True, null=True)
    cumulative_values = JSONField(blank=True, null=True)
    cumulative_values_hpm = JSONField(blank=True, null=True, default={})
    tag_age = models.ForeignKey(IndicatorTag, blank=True, null=True, related_name='+')
    tag_gender = models.ForeignKey(IndicatorTag, blank=True, null=True, related_name='+')
    tag_nationality = models.ForeignKey(IndicatorTag, blank=True, null=True, related_name='+')
    tag_disability = models.ForeignKey(IndicatorTag, blank=True, null=True, related_name='+')
    hpm_indicator = models.BooleanField(default=False)
    separator_indicator = models.BooleanField(default=False)
    none_ai_indicator = models.BooleanField(default=False)
    sequence = models.IntegerField(blank=True, null=True)
    funded_by = models.CharField(max_length=254, blank=True, null=True)
    measurement_type = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        choices=Choices(
            ('numeric', 'Numeric'),
            ('percentage', 'Percentage'),
            ('percentage_x', 'Percentage multiple X'),
            ('weighting', 'Weighting'),
        )
    )
    denominator_multiplication = models.IntegerField(blank=True, null=True, default=0)
    values_live = JSONField(blank=True, null=True, default={})
    values_gov_live = JSONField(blank=True, null=True, default={})
    values_partners_live = JSONField(blank=True, null=True, default={})
    values_partners_gov_live = JSONField(blank=True, null=True, default={})
    cumulative_values_live = JSONField(blank=True, null=True, default={})

    def __unicode__(self):
        return self.name

    @property
    def get_ai_indicator(self):
        if len(str(self.ai_id)) == 10:
            return self.ai_id
        return '{0:0>10}'.format(self.ai_id)

    @property
    def cumulative_per(self):
        if 'months' in self.cumulative_values and self.target:
            if isinstance(self.cumulative_values['months'], dict):
                return 0
            return round((self.cumulative_values['months'] * 100.0) / self.target, 2)
        return 0

    @property
    def section_id(self):
        if self.activity and self.activity.database.section:
            return self.activity.database.section_id

    @property
    def section(self):
        if self.activity and self.activity.database.section:
            return self.activity__database__section

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
    form = models.CharField(max_length=1000, blank=True, null=True)
    form_category = models.CharField(max_length=1000, blank=True, null=True)
    ai_indicator = models.ForeignKey(Indicator, blank=True, null=True)
    indicator_category = models.CharField(max_length=1000, blank=True, null=True)
    indicator_id = models.CharField(max_length=250, blank=True, null=True)
    indicator_name = models.CharField(max_length=1000, blank=True, null=True)
    indicator_details = models.CharField(max_length=1000, blank=True, null=True)
    indicator_master = models.CharField(max_length=250, blank=True, null=True)
    indicator_info = models.CharField(max_length=250, blank=True, null=True)
    indicator_units = models.CharField(max_length=250, blank=True, null=True)
    indicator_value = models.FloatField(blank=True, null=True)
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
    partner_ai = models.ForeignKey(Partner, blank=True, null=True, related_name='+')
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
    pending = models.BooleanField(default=False)


class ActivityReportLive(ActivityReport):

    class Meta:
        ordering = ['id']


class LiveActivityReport(TimeStampedModel):
    end_date = models.CharField(max_length=250, blank=True, null=True)
    form = models.CharField(max_length=1000, blank=True, null=True)
    form_category = models.CharField(max_length=1000, blank=True, null=True)
    ai_indicator = models.ForeignKey(Indicator, blank=True, null=True)
    indicator_category = models.CharField(max_length=1000, blank=True, null=True)
    indicator_id = models.CharField(max_length=250, blank=True, null=True)
    indicator_name = models.CharField(max_length=1000, blank=True, null=True)
    indicator_details = models.CharField(max_length=1000, blank=True, null=True)
    indicator_master = models.CharField(max_length=250, blank=True, null=True)
    indicator_info = models.CharField(max_length=250, blank=True, null=True)
    indicator_units = models.CharField(max_length=250, blank=True, null=True)
    indicator_value = models.FloatField(blank=True, null=True)
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
    partner_ai = models.ForeignKey(Partner, blank=True, null=True, related_name='+')
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
    pending = models.BooleanField(default=False)

    class Meta:
        ordering = ['id']
        # models.Index(fields=['indicator_id', 'partner_id', 'start_date', 'location_adminlevel_governorate_code', 'funded_by'])


class AdminLevels(models.Model):

    name = models.CharField(max_length=650)


class LocationTypes(models.Model):

    name = models.CharField(max_length=650)
    parent = models.ForeignKey('self', blank=True, null=True)


class AdminLevelEntities(models.Model):

    code = models.CharField(max_length=250)
    name = models.CharField(max_length=650)
    parent = models.ForeignKey('self', blank=True, null=True)
    level = models.ForeignKey(AdminLevels, blank=True, null=True)
    bounds = JSONField(blank=True, null=True)


class Locations(models.Model):

    code = models.CharField(max_length=250)
    name = models.CharField(max_length=650)
    type = models.ForeignKey(LocationTypes, blank=True, null=True)
    admin_entities = JSONField(blank=True, null=True)
    longitude = models.CharField(max_length=250)
    latitude = models.CharField(max_length=250)
    entities = models.ManyToManyField(AdminLevelEntities, blank=True, related_name='entity_locations')
