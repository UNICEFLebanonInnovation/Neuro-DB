from __future__ import unicode_literals

from django.db import models
from model_utils import Choices
from django.contrib.postgres.fields import JSONField,  ArrayField


class Programme(models.Model):
    year = models.CharField(
        max_length=45,
        blank=False,
        null=False,
    )
    db_url = models.CharField(
        max_length=750,
        blank=False,
        null=False,
    )
    db_username = models.CharField(
        max_length=100,
        blank=False,
        null=False,
    )
    db_pwd = models.CharField(
        max_length=750,
        blank=False,
        null=False,
    )

    def __unicode__(self):
        return self.year


class Assessment(models.Model):

    REGISTRATION_STATUS = Choices(
        ('Registered', 'Registered'),
        ('Recorded', 'Recorded'),
        ('Unregistered', 'Unregistered'),
    )
    LOCATION_TYPE = Choices(
        ('CS', 'CS'),
        ('IS', 'IS'),
    )
    CARD_DISTRIBUTION_STATUS = Choices(
        ('Distributed', 'Distributed'),
        ('Not Distributed', 'Not Distributed'),
    )
    CARD_LOADED = Choices(
        ('Yes', 'Yes'),
        ('No', 'No'),
    )

    _id = models.CharField(
        max_length=45,
        unique=True,
        primary_key=True
    )
    _rev = models.CharField(
        max_length=45,
        blank=True,
        null=True,
    )
    programme = models.ForeignKey(Programme, blank=True, null=True)
    assistance_type = JSONField(blank=True, null=True)
    barcode_num = models.CharField(
        max_length=45,
        blank=True,
        null=True,
    )
    channels = JSONField(blank=True, null=True)
    child_list = JSONField(blank=True, null=True)

    completed = models.BooleanField(default=False)
    completion_date = models.CharField(
        max_length=45,
        blank=True,
        null=True,
    )
    creation_date = models.CharField(
        max_length=45,
        blank=True,
        null=True,
    )
    criticality = models.CharField(
        max_length=45,
        blank=True,
        null=True,
    )
    disabilities = models.CharField(
        max_length=45,
        blank=True,
        null=True,
    )
    dob = models.CharField(
        max_length=45,
        blank=True,
        null=True,
    )
    family_count = models.CharField(
        max_length=45,
        blank=True,
        null=True,
    )
    family_list = JSONField(blank=True, null=True)
    family_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )
    first_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )
    gender = models.CharField(
        max_length=45,
        blank=True,
        null=True,
    )
    history = JSONField(blank=True, null=True)
    id_type = models.CharField(
        max_length=45,
        blank=True,
        null=True,
    )
    location = JSONField(blank=True, null=True)
    location_distribution = JSONField(blank=True, null=True)
    marital_status = models.CharField(
        max_length=45,
        blank=True,
        null=True,
    )
    middle_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )
    mothers_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )
    moving_location = models.CharField(
        max_length=45,
        blank=True,
        null=True,
    )
    new_cadastral = models.CharField(
        max_length=45,
        blank=True,
        null=True,
    )
    new_district = models.CharField(
        max_length=45,
        blank=True,
        null=True,
    )
    official_id = models.CharField(
        max_length=45,
        blank=True,
        null=True,
    )
    over18 = models.CharField(
        max_length=45,
        blank=True,
        null=True,
    )
    partner_name = models.CharField(
        max_length=45,
        blank=True,
        null=True,
    )
    phone_number = models.CharField(
        max_length=45,
        blank=True,
        null=True,
    )
    phone_owner = models.CharField(
        max_length=45,
        blank=True,
        null=True,
    )
    principal_applicant = models.CharField(
        max_length=45,
        blank=True,
        null=True,
    )
    relationship_type = models.CharField(
        max_length=45,
        blank=True,
        null=True,
    )
    type = models.CharField(
        max_length=45,
        blank=True,
        null=True,
    )

    registration_status = models.CharField(
        max_length=45,
        blank=True,
        null=True,
        choices=REGISTRATION_STATUS
    )
    location_type = models.CharField(
        max_length=45,
        blank=True,
        null=True,
    )
    governorate = models.CharField(
        max_length=45,
        blank=True,
        null=True,
    )
    district = models.CharField(
        max_length=45,
        blank=True,
        null=True,
    )
    cadastral = models.CharField(
        max_length=45,
        blank=True,
        null=True,
    )
    latitude = models.CharField(
        max_length=45,
        blank=True,
        null=True,
    )
    longitude = models.CharField(
        max_length=45,
        blank=True,
        null=True,
    )
    p_code = models.CharField(
        max_length=45,
        blank=True,
        null=True,
    )
    p_code_name = models.CharField(
        max_length=45,
        blank=True,
        null=True,
    )
    site_type = models.CharField(
        max_length=45,
        blank=True,
        null=True,
    )

    total_children = models.IntegerField(
        blank=True,
        null=True,
    )
    card_distributed = models.CharField(
        max_length=45,
        blank=True,
        null=True,
        choices=CARD_DISTRIBUTION_STATUS
    )
    card_loaded = models.CharField(
        max_length=45,
        blank=True,
        null=True,
        choices=CARD_LOADED
    )
    comments = JSONField(blank=True, null=True)

    _0_to_3_months = models.IntegerField(
        blank=True,
        null=True,
    )
    _3_to_12_months = models.IntegerField(
        blank=True,
        null=True,
    )
    _1_year_old = models.IntegerField(
        blank=True,
        null=True,
    )
    _2_years_old = models.IntegerField(
        blank=True,
        null=True,
    )
    _3_years_old = models.IntegerField(
        blank=True,
        null=True,
    )
    _4_years_old = models.IntegerField(
        blank=True,
        null=True,
    )
    _5_years_old = models.IntegerField(
        blank=True,
        null=True,
    )
    _6_years_old = models.IntegerField(
        blank=True,
        null=True,
    )
    _7_years_old = models.IntegerField(
        blank=True,
        null=True,
    )
    _8_years_old = models.IntegerField(
        blank=True,
        null=True,
    )
    _9_years_old = models.IntegerField(
        blank=True,
        null=True,
    )
    _10_years_old = models.IntegerField(
        blank=True,
        null=True,
    )
    _11_years_old = models.IntegerField(
        blank=True,
        null=True,
    )
    _12_years_old = models.IntegerField(
        blank=True,
        null=True,
    )
    _13_years_old = models.IntegerField(
        blank=True,
        null=True,
    )
    _14_years_old = models.IntegerField(
        blank=True,
        null=True,
    )
    male = models.IntegerField(
        blank=True,
        null=True,
    )
    female = models.IntegerField(
        blank=True,
        null=True,
    )
    _3_months_kit = models.IntegerField(
        blank=True,
        null=True,
    )
    _12_months_kit = models.IntegerField(
        blank=True,
        null=True,
    )
    _2_years_kit = models.IntegerField(
        blank=True,
        null=True,
    )
    _3_years_kit = models.IntegerField(
        blank=True,
        null=True,
    )
    _5_years_kit = models.IntegerField(
        blank=True,
        null=True,
    )
    _7_years_kit = models.IntegerField(
        blank=True,
        null=True,
    )
    _9_years_kit = models.IntegerField(
        blank=True,
        null=True,
    )
    _12_years_kit = models.IntegerField(
        blank=True,
        null=True,
    )
    _14_years_kit = models.IntegerField(
        blank=True,
        null=True,
    )
    _3_months_kit_completed = models.IntegerField(
        blank=True,
        null=True,
    )
    _12_months_kit_completed = models.IntegerField(
        blank=True,
        null=True,
    )
    _2_years_kit_completed = models.IntegerField(
        blank=True,
        null=True,
    )
    _3_years_kit_completed = models.IntegerField(
        blank=True,
        null=True,
    )
    _5_years_kit_completed = models.IntegerField(
        blank=True,
        null=True,
    )
    _7_years_kit_completed = models.IntegerField(
        blank=True,
        null=True,
    )
    _9_years_kit_completed = models.IntegerField(
        blank=True,
        null=True,
    )
    _12_years_kit_completed = models.IntegerField(
        blank=True,
        null=True,
    )
    _14_years_kit_completed  = models.IntegerField(
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ['id_type']
        verbose_name_plural = "Assessments"

    @property
    def amount(self):
        return 0

    def get_id(self):
        return self._id

    def get_0_to_3_months(self):
        return self._0_to_3_months

    def get_3_to_12_months(self):
        return self._3_to_12_months

    def get_1_year_old(self):
        return self._1_year_old

    def get_2_years_old(self):
        return self._2_years_old

    def get_3_years_old(self):
        return self._3_years_old

    def get_4_years_old(self):
        return self._4_years_old

    def get_5_years_old(self):
        return self._5_years_old

    def get_6_years_old(self):
        return self._6_years_old

    def get_7_years_old(self):
        return self._7_years_old

    def get_8_years_old(self):
        return self._8_years_old

    def get_9_years_old(self):
        return self._9_years_old

    def get_10_years_old(self):
        return self._10_years_old

    def get_11_years_old(self):
        return self._11_years_old

    def get_12_years_old(self):
        return self._12_years_old

    def get_13_years_old(self):
        return self._13_years_old

    def get_14_years_old(self):
        return self._14_years_old

    def get_3_months_kit(self):
        return self._3_months_kit

    def get_12_months_kit(self):
        return self._12_months_kit

    def get_2_years_kit(self):
        return self._2_years_kit

    def get_3_years_kit(self):
        return self._3_years_kit

    def get_5_years_kit(self):
        return self._5_years_kit

    def get_7_years_kit(self):
        return self._7_years_kit

    def get_9_years_kit(self):
        return self._9_years_kit

    def get_12_years_kit(self):
        return self._12_years_kit

    def get_14_years_kit(self):
        return self._14_years_kit

    def get_3_months_kit_completed(self):
        return self._3_months_kit_completed

    def get_12_months_kit_completed(self):
        return self._12_months_kit_completed

    def get_2_years_kit_completed(self):
        return self._2_years_kit_completed

    def get_3_years_kit_completed(self):
        return self._3_years_kit_completed

    def get_5_years_kit_completed(self):
        return self._5_years_kit_completed

    def get_7_years_kit_completed(self):
        return self._7_years_kit_completed

    def get_9_years_kit_completed(self):
        return self._9_years_kit_completed

    def get_12_years_kit_completed(self):
        return self._12_years_kit_completed

    def get_14_years_kit_completed(self):
        return self._14_years_kit_completed

    def set_0_to_3_months(self, value):
        self._0_to_3_months = value

    def set_3_to_12_months(self, value):
        self._3_to_12_months = value

    def set_1_year_old(self, value):
        self._1_year_old = value

    def set_2_years_old(self, value):
        self._2_years_old = value

    def set_3_years_old(self, value):
        self._3_years_old = value

    def set_4_years_old(self, value):
        self._4_years_old = value

    def set_5_years_old(self, value):
        self._5_years_old = value

    def set_6_years_old(self, value):
        self._6_years_old = value

    def set_7_years_old(self, value):
        self._7_years_old = value

    def set_8_years_old(self, value):
        self._8_years_old = value

    def set_9_years_old(self, value):
        self._9_years_old = value

    def set_10_years_old(self, value):
        self._10_years_old = value

    def set_11_years_old(self, value):
        self._11_years_old = value

    def set_12_years_old(self, value):
        self._12_years_old = value

    def set_13_years_old(self, value):
        self._13_years_old = value

    def set_14_years_old(self, value):
        self._14_years_old = value

    def set_3_months_kit(self, value):
        self._3_months_kit = value

    def set_12_months_kit(self, value):
        self._12_months_kit = value

    def set_2_years_kit(self, value):
        self._2_years_kit = value

    def set_3_years_kit(self, value):
        self._3_years_kit = value

    def set_5_years_kit(self, value):
        self._5_years_kit = value

    def set_7_years_kit(self, value):
        self._7_years_kit = value

    def set_9_years_kit(self, value):
        self._9_years_kit = value

    def set_12_years_kit(self, value):
        self._12_years_kit = value

    def set_14_years_kit(self, value):
        self._14_years_kit = value

    def set_3_months_kit_completed(self, value):
        self._3_months_kit_completed = value

    def set_12_months_kit_completed(self, value):
        self._12_months_kit_completed = value

    def set_2_years_kit_completed(self, value):
        self._2_years_kit_completed = value

    def set_3_years_kit_completed(self, value):
        self._3_years_kit_completed = value

    def set_5_years_kit_completed(self, value):
        self._5_years_kit_completed = value

    def set_7_years_kit_completed(self, value):
        self._7_years_kit_completed = value

    def set_9_years_kit_completed(self, value):
        self._9_years_kit_completed = value

    def set_12_years_kit_completed(self, value):
        self._12_years_kit_completed = value

    def set_14_years_kit_completed(self, value):
        self._14_years_kit_completed = value

    @property
    def location_p_code(self):
        if self.location and self.location['p_code']:
            return self.location['p_code']
        return self.p_code

    @property
    def location_p_code_name(self):
        if self.location and self.location['p_code_name']:
            return self.location['p_code_name']
        return self.p_code_name

    @property
    def location_district(self):
        if self.location and self.location['cadastral']:
            return self.location['cadastral']
        return ''

    @property
    def location_cadastral(self):
        if self.location and self.location['cadastral']:
            return self.location['cadastral']
        return ''

    @property
    def location_latitude(self):
        if self.location and self.location['latitude']:
            return self.location['latitude']
        return ''

    @property
    def location_longitude(self):
        if self.location and self.location['longitude']:
            return self.location['longitude']
        return ''

    @property
    def locations_type(self):
        if self.location and self.location['location_type']:
            return self.location['location_type']
        return ''

    def __unicode__(self):
        return self._id
