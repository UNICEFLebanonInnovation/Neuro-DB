from __future__ import unicode_literals

from django.db import models

from model_utils.choices import Choices
from django.conf import settings


class PartnerOrganization(models.Model):

    partner_type = models.CharField(
        max_length=50,
        choices=Choices(
            u'Bilateral / Multilateral',
            u'Civil Society Organization',
            u'Government',
            u'UN Agency',
        )
    )
    cso_type = models.CharField(
        max_length=50,
        choices=Choices(
            u'International',
            u'National',
            u'Community Based Organisation',
            u'Academic Institution',
        ),
        verbose_name=u'CSO Type',
        blank=True, null=True
    )
    name = models.CharField(
        max_length=255,
        verbose_name='Full Name',
        help_text=u'Please make sure this matches the name you enter in VISION'
    )
    short_name = models.CharField(
        max_length=50,
        blank=True
    )
    description = models.CharField(
        max_length=256,
        blank=True
    )
    shared_partner = models.CharField(
        help_text=u'Partner shared with UNDP or UNFPA?',
        choices=Choices(
            u'No',
            u'with UNDP',
            u'with UNFPA',
            u'with UNDP & UNFPA',
        ),
        default=u'No',
        max_length=50, blank=True,
    )
    address = models.TextField(
        blank=True,
        null=True
    )
    email = models.CharField(
        max_length=255,
        blank=True, null=True
    )
    phone_number = models.CharField(
        max_length=32,
        blank=True, null=True
    )
    vendor_number = models.CharField(
        blank=True,
        null=True,
        max_length=30
    )
    alternate_id = models.IntegerField(
        blank=True,
        null=True
    )
    alternate_name = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )
    rating = models.CharField(
        max_length=50,
        blank=True, null=True,
        verbose_name=u'Risk Rating'
    )

    class Meta:
        ordering = ['name']
        unique_together = ('name', 'vendor_number')

    def __unicode__(self):
        return self.name


class PartnerStaffMember(models.Model):

    partner = models.ForeignKey(PartnerOrganization)
    title = models.CharField(max_length=64)
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    email = models.CharField(max_length=128, blank=True)
    phone = models.CharField(max_length=64, blank=False)
    active = models.BooleanField(
        default=True
    )

    def __unicode__(self):
        return u'{} {}'.format(
            self.first_name,
            self.last_name
        )


class Agreement(models.Model):

    PCA = u'PCA'
    MOU = u'MOU'
    SSFA = u'SSFA'
    IC = u'IC'
    AWP = u'AWP'
    AGREEMENT_TYPES = (
        (PCA, u"Programme Cooperation Agreement"),
        (SSFA, u'Small Scale Funding Agreement'),
        (MOU, u'Memorandum of Understanding'),
        (IC, u'Institutional Contract'),
        (AWP, u"Work Plan"),
    )

    partner = models.ForeignKey(
        PartnerOrganization,
        blank=True,null=True
    )
    partner_name = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )
    agreement_type = models.CharField(
        max_length=10,
        choices=AGREEMENT_TYPES
    )
    agreement_number = models.CharField(
        max_length=45,
        blank=True,
        verbose_name=u'Reference Number'
    )
    start = models.DateField(null=True, blank=True)
    end = models.DateField(null=True, blank=True)

    signed_by_unicef_date = models.DateField(null=True, blank=True)
    signed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='signed_pcas',
        null=True, blank=True
    )

    signed_by_partner_date = models.DateField(null=True, blank=True)
    partner_manager = models.ForeignKey(
        PartnerStaffMember,
        verbose_name=u'Signed by partner',
        blank=True, null=True,
    )

    def __unicode__(self):
        return u'{} for {} ({} - {})'.format(
            self.agreement_type,
            self.partner_name,
            self.start.strftime('%d-%m-%Y') if self.start else '',
            self.end.strftime('%d-%m-%Y') if self.end else ''
        )


class PCA(models.Model):

    IN_PROCESS = u'in_process'
    ACTIVE = u'active'
    IMPLEMENTED = u'implemented'
    CANCELLED = u'cancelled'
    PCA_STATUS = (
        (IN_PROCESS, u"In Process"),
        (ACTIVE, u"Active"),
        (IMPLEMENTED, u"Implemented"),
        (CANCELLED, u"Cancelled"),
    )
    PD = u'PD'
    SHPD = u'SHPD'
    AWP = u'AWP'
    SSFA = u'SSFA'
    IC = u'IC'
    PARTNERSHIP_TYPES = (
        (PD, u'Programme Document'),
        (SHPD, u'Simplified Humanitarian Programme Document'),
        (AWP, u'Cash Transfers to Government'),
        (SSFA, u'SSFA TOR'),
        (IC, u'IC TOR'),
    )

    partner = models.ForeignKey(
        PartnerOrganization,
        blank=True, null=True
    )
    partner_name = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )
    agreement = models.ForeignKey(
        Agreement,
        related_name='interventions',
        blank=True, null=True,
    )
    document_type = models.CharField(
        choices=PARTNERSHIP_TYPES,
        default=PD,
        blank=True, null=True,
        max_length=255,
        verbose_name=u'Document type'
    )
    country_programme = models.CharField(
        max_length=32,
        blank=True, null=True,
        help_text=u'Which result structure does this partnership report under?'
    )
    number = models.CharField(
        max_length=45L,
        blank=True, null=True,
        verbose_name=u'Reference Number'
    )
    title = models.CharField(max_length=256L)
    project_type = models.CharField(
        max_length=20,
        blank=True, null=True,
        choices=Choices(
            u'Bulk Procurement',
            u'Construction Project',
        )
    )
    status = models.CharField(
        max_length=32,
        blank=True,
        choices=PCA_STATUS,
        default=u'in_process',
        help_text=u'In Process = In discussion with partner, '
                  u'Active = Currently ongoing, '
                  u'Implemented = completed, '
                  u'Cancelled = cancelled or not approved'
    )

    # dates
    start= models.DateField(
        null=True, blank=True,
        verbose_name='Partnership start date',
        help_text=u'The date the Intervention will start'
    )
    end = models.DateField(
        null=True, blank=True,
        verbose_name='Partnership end date',
        help_text=u'The date the Intervention will end'
    )
    initiation_date = models.DateField(
        null=True, blank=True,
        verbose_name=u'Submission Date',
        help_text=u'The date the partner submitted complete partnership documents to Unicef',
    )
    submission_date = models.DateField(
        verbose_name=u'Submission Date to PRC',
        help_text=u'The date the documents were submitted to the PRC',
        null=True, blank=True,
    )
    review_date = models.DateField(
        verbose_name=u'Review date by PRC',
        help_text=u'The date the PRC reviewed the partnership',
        null=True, blank=True,
    )
    signed_by_unicef_date = models.DateField(null=True, blank=True)
    signed_by_partner_date = models.DateField(null=True, blank=True)

    # managers and focal points
    unicef_manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='approved_partnerships',
        verbose_name=u'Signed by',
        blank=True, null=True
    )
    unicef_managers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name='Unicef focal points',
        blank=True
    )
    partner_manager = models.ForeignKey(
        PartnerStaffMember,
        verbose_name=u'Signed by partner',
        related_name='signed_partnerships',
        blank=True, null=True,
    )
    partner_focal_point = models.ForeignKey(
        PartnerStaffMember,
        related_name='my_partnerships',
        blank=True, null=True,
    )

    fr_number = models.CharField(max_length=50, null=True, blank=True)
    planned_visits = models.IntegerField(default=0)

    sectors = models.CharField(max_length=255, null=True, blank=True)
    current = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Intervention'
        verbose_name_plural = 'Interventions'
        ordering = ['-created_at']

    def __unicode__(self):
        return u'{}: {}'.format(
            self.partner_name,
            self.number
        )

    @property
    def sector_id(self):
        if self.sector_children:
            return self.sector_children[0].id
        return 0

    @property
    def sector_names(self):
        return u', '.join(self.sector_children.values_list('name', flat=True))

    @property
    def amendment_num(self):
        return self.amendments_log.all().count()

    @property
    def total_unicef_cash(self):

        if self.budget_log.exists():
            return sum([b['unicef_cash'] for b in
                 self.budget_log.values('created', 'year', 'unicef_cash').
                 order_by('year', '-created').distinct('year').all()
                 ])
        return 0

    @property
    def total_budget(self):

        if self.budget_log.exists():
            return sum([b['unicef_cash'] + b['in_kind_amount'] + b['partner_contribution'] for b in
                 self.budget_log.values('created', 'year', 'unicef_cash', 'in_kind_amount', 'partner_contribution').
                 order_by('year','-created').distinct('year').all()])
        return 0
