from __future__ import unicode_literals

import logging
import datetime
import json
from model_utils.choices import Choices
from django.conf import settings
from django.contrib.postgres.fields import ArrayField, JSONField
from django.db import connection, models
from django.utils.translation import ugettext, ugettext_lazy as _
from django_fsm import FSMField, transition
from model_utils import Choices
from model_utils.models import TimeStampedModel
from ordered_model.models import OrderedModel


from internos.locations.models import Location

log = logging.getLogger(__name__)


class PartnerOrganization(models.Model):

    AGENCY_CHOICES = Choices(
        ('DPKO', 'DPKO'),
        ('ECA', 'ECA'),
        ('ECLAC', 'ECLAC'),
        ('ESCWA', 'ESCWA'),
        ('FAO', 'FAO'),
        ('ILO', 'ILO'),
        ('IOM', 'IOM'),
        ('OHCHR', 'OHCHR'),
        ('UN', 'UN'),
        ('UN Women', 'UN Women'),
        ('UNAIDS', 'UNAIDS'),
        ('UNDP', 'UNDP'),
        ('UNESCO', 'UNESCO'),
        ('UNFPA', 'UNFPA'),
        ('UN - Habitat', 'UN - Habitat'),
        ('UNHCR', 'UNHCR'),
        ('UNODC', 'UNODC'),
        ('UNOPS', 'UNOPS'),
        ('UNRWA', 'UNRWA'),
        ('UNSC', 'UNSC'),
        ('UNU', 'UNU'),
        ('WB', 'WB'),
        ('WFP', 'WFP'),
        ('WHO', 'WHO')
    )

    etl_id = models.CharField(
        unique=True,
        max_length=50,
        verbose_name='eTools ID'
    )
    partner_type = models.CharField(
        max_length=50,
        choices=Choices(
            u'Bilateral / Multilateral',
            u'Civil Society Organization',
            u'Government',
            u'UN Agency',
        )
    )
    shared_with = ArrayField(
        models.CharField(max_length=20, blank=True, choices=AGENCY_CHOICES),
        verbose_name=_("Shared Partner"),
        blank=True,
        null=True
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
    deleted_flag = models.BooleanField(default=False)
    blocked = models.BooleanField(default=False)
    hidden = models.BooleanField(default=False)
    comments = models.TextField(blank=True, null=True)

    staff_members = JSONField(blank=True, null=True)
    assessments = JSONField(blank=True, null=True)
    planned_engagement = JSONField(blank=True, null=True)
    hact_values = JSONField(blank=True, null=True)
    hact_min_requirements = JSONField(blank=True, null=True)
    planned_visits = JSONField(blank=True, null=True)
    core_values_assessments = JSONField(blank=True, null=True)
    flags = JSONField(blank=True, null=True)

    type_of_assessment = models.CharField(max_length=250, blank=True, null=True)
    last_assessment_date = models.DateField(null=True, blank=True)
    core_values_assessment_date = models.DateField(null=True, blank=True)

    total_ct_cp = models.CharField(max_length=250, blank=True, null=True)
    total_ct_cy = models.CharField(max_length=250, blank=True, null=True)
    net_ct_cy = models.CharField(max_length=250, blank=True, null=True)
    reported_cy = models.CharField(max_length=250, blank=True, null=True)
    total_ct_ytd = models.CharField(max_length=250, blank=True, null=True)

    @property
    def programmatic_visits(self):
        today = datetime.date.today()
        travels = self.travelactivity_set.filter(travel_type='programmatic visit',
                                                 date__year=today.year).exclude(
            travel__status=Travel.CANCELLED).exclude(
            travel__status=Travel.REJECTED).order_by('date').only(
            'id',
            'partnership_id',
            'partnership__number',
            'travel__status',
            'travel__attachments_sets',
        ).values(
            'id',
            'partnership_id',
            'partnership__number',
            'travel__status',
            'travel__attachments_sets',
        )
        return {
            'nbr_visits': travels.count(),
            'nbr_planned': travels.filter(travel__status=Travel.PLANNED).count(),
            'nbr_submitted': travels.filter(travel__status=Travel.SUBMITTED).count(),
            'nbr_approved': travels.filter(travel__status=Travel.APPROVED).count(),
            'nbr_completed': travels.filter(travel__status=Travel.COMPLETED).count(),
            # 'nbr_cancelled': travels.filter(travel__status=Travel.CANCELLED).count(),
            # 'nbr_rejected': travels.filter(travel__status=Travel.REJECTED).count(),
            'last_visit': travels.last(),
            'audits': travels,
            'completed': travels.filter(travel__status=Travel.COMPLETED),
        }

    @property
    def audits(self):
        today = datetime.date.today()
        items = self.engagement_set.filter(engagement_type=Engagement.TYPE_AUDIT,
                                           start_date__year=today.year).exclude(status=Engagement.CANCELLED).order_by('start_date').only(
            'id',
            'findings_sets',
            'internal_controls',
        ).values(
            'id',
            'findings_sets',
            'internal_controls',
        )
        return {
            'nbr_audits': items.count(),
            'last_audit': items.last(),
            'audits': items
        }

    @property
    def micro_assessments(self):
        today = datetime.date.today()
        items = self.engagement_set.filter(engagement_type=Engagement.TYPE_MICRO_ASSESSMENT
                                           ).exclude(status=Engagement.CANCELLED).order_by('start_date').only(
            'id',
            'findings_sets',
            'internal_controls',
        ).values(
            'id',
            'findings_sets',
            'internal_controls',
        )
        # items = self.engagement_set.filter(engagement_type=Engagement.TYPE_MICRO_ASSESSMENT, start_date__year=today.year).order_by('start_date')
        return {
            'nbr_audits': items.count(),
            'last_audit': items.last(),
            'audits': items
        }

    @property
    def spot_checks(self):
        today = datetime.date.today()
        items = self.engagement_set.filter(engagement_type=Engagement.TYPE_SPOT_CHECK).exclude(status=Engagement.CANCELLED).only(
            'id',
            'findings_sets',
            'internal_controls',
        ).order_by('start_date').values(
            'id',
            'findings_sets',
            'internal_controls',
        )
        # items = self.engagement_set.filter(engagement_type=Engagement.TYPE_SPOT_CHECK, start_date__year=today.year).order_by('start_date')
        return {
            'nbr_audits': items.count(),
            'last_audit': items.last(),
            'audits': items
        }

    @property
    def special_audits(self):
        today = datetime.date.today()
        items = self.engagement_set.filter(engagement_type=Engagement.TYPE_SPECIAL_AUDIT).exclude(status=Engagement.CANCELLED).only(
            'id',
            'findings_sets',
            'internal_controls',
        ).order_by('start_date').values(
            'id',
            'findings_sets',
            'internal_controls',
        )
        # items = self.engagement_set.filter(engagement_type=Engagement.TYPE_SPECIAL_AUDIT, start_date__year=today.year).order_by('start_date')
        return {
            'nbr_audits': items.count(),
            'last_audit': items.last(),
            'audits': items
        }

    @property
    def interventions_details(self):
        data = []
        now = datetime.datetime.now()
        interventions = self.interventions.filter(end__year=now.year).order_by('start').only(
            'etl_id',
            'number',
            'start',
            'end',
            'document_type',
            'total_unicef_budget',
            'budget_currency',
            'total_budget',
            'offices_names',
            'location_p_codes'
        ).values(
            'etl_id',
            'number',
            'start',
            'end',
            'document_type',
            'total_unicef_budget',
            'budget_currency',
            'total_budget',
            'offices_names',
            'location_p_codes'
        )

        for item in interventions.iterator():
            data.append({
                'etl_id': item['etl_id'],
                'number': item['number'],
                'start': item['start'],
                'end': item['end'],
                'document_type': item['document_type'],
                'total_unicef_budget': item['total_unicef_budget'],
                'budget_currency': item['budget_currency'],
                'total_budget': item['total_budget'],
                'offices_names': item['offices_names'],
                'location_p_codes': item['location_p_codes']
            })
        return data

    @property
    def detailed_info(self):
        return {
            'id': self.etl_id,
            'name': self.name,
            'short_name': self.short_name,
            'description': self.description,
            'type': self.partner_type,
            'rating': self.rating,
            'interventions': self.interventions_details,
            'programmatic_visits': self.programmatic_visits,
            'audits': self.audits,
            'micro_assessments': self.micro_assessments,
            'spot_checks': self.spot_checks,
            'special_audits': self.special_audits,
        }

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
    etl_id = models.CharField(
        unique=True,
        max_length=50,
        verbose_name='eTools ID'
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
    ENDED = u'ended'
    PCA_STATUS = (
        (IN_PROCESS, u"In Process"),
        (ACTIVE, u"Active"),
        (IMPLEMENTED, u"Implemented"),
        (CANCELLED, u"Cancelled"),
        (ENDED, u"Ended"),
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
    etl_id = models.CharField(
        unique=True,
        max_length=50,
        verbose_name='eTools ID'
    )
    partner = models.ForeignKey(
        PartnerOrganization,
        blank=True, null=True,
        related_name='interventions'
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
        max_length=45,
        blank=True, null=True,
        verbose_name=u'Reference Number'
    )
    title = models.CharField(max_length=256)
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
        # choices=PCA_STATUS,
        default=u'in_process',
        help_text=u'In Process = In discussion with partner, '
                  u'Active = Currently ongoing, '
                  u'Implemented = completed, '
                  u'Cancelled = cancelled or not approved'
    )

    # dates
    start = models.DateField(
        null=True, blank=True,
        verbose_name='Partnership start date',
        help_text=u'The date the Intervention will start'
    )
    end = models.DateField(
        null=True, blank=True,
        verbose_name='Partnership end date',
        help_text=u'The date the Intervention will end'
    )
    end_date = models.DateField(
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
    offices_names = models.CharField(max_length=255, null=True, blank=True)
    current = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_budget = models.CharField(max_length=255, null=True, blank=True)
    fr_currency = models.CharField(max_length=255, null=True, blank=True)
    frs_total_intervention_amt = models.CharField(max_length=255, null=True, blank=True)
    frs_latest_end_date = models.CharField(max_length=255, null=True, blank=True)
    frs_total_frs_amt = models.CharField(max_length=255, null=True, blank=True)
    fr_currencies_are_consistent = models.CharField(max_length=255, null=True, blank=True)
    unicef_cash = models.CharField(max_length=255, null=True, blank=True)
    multi_curr_flag = models.CharField(max_length=255, null=True, blank=True)
    actual_amount = models.CharField(max_length=255, null=True, blank=True)
    frs_total_outstanding_amt = models.CharField(max_length=255, null=True, blank=True)
    budget_currency = models.CharField(max_length=255, null=True, blank=True)
    frs_earliest_start_date = models.CharField(max_length=255, null=True, blank=True)
    cso_contribution = models.CharField(max_length=255, null=True, blank=True)
    all_currencies_are_consistent = models.CharField(max_length=255, null=True, blank=True)
    total_unicef_budget = models.CharField(max_length=255, null=True, blank=True)
    grants = ArrayField(models.CharField(max_length=200), blank=True, null=True)
    unicef_focal_points = ArrayField(models.CharField(max_length=200), blank=True, null=True)
    section_names = ArrayField(models.CharField(max_length=200), blank=True, null=True)
    sections = ArrayField(models.CharField(max_length=200), blank=True, null=True)
    donors = ArrayField(models.CharField(max_length=200), blank=True, null=True)
    donor_codes = ArrayField(models.CharField(max_length=200), blank=True, null=True)
    flagged_sections = ArrayField(models.CharField(max_length=200), blank=True, null=True)
    location_p_codes = ArrayField(models.CharField(max_length=200), blank=True, null=True)
    locations = models.ManyToManyField(
        'locations.Location',
        related_name='+',
        blank=True
    )
    offices = ArrayField(models.CharField(max_length=200), blank=True, null=True)
    cp_outputs = ArrayField(models.CharField(max_length=200), blank=True, null=True)
    planned_budget = ArrayField(models.CharField(max_length=200), blank=True, null=True)
    amendments = ArrayField(models.CharField(max_length=200), blank=True, null=True)
    result_links = ArrayField(models.CharField(max_length=200), blank=True, null=True)
    location_names = ArrayField(models.CharField(max_length=200), blank=True, null=True)
    planned_visits_list = ArrayField(models.CharField(max_length=200), blank=True, null=True)
    frs_details = JSONField(blank=True, null=True, default={})
    donors_set = JSONField(blank=True, null=True, default={})
    activities = models.ManyToManyField('activityinfo.activity', blank=True, related_name='interventions')

    class Meta:
        verbose_name = 'Intervention'
        verbose_name_plural = 'Interventions'
        ordering = ['-partner_name']

    def __unicode__(self):
        return u'{}: {} - {}'.format(
            self.partner_name,
            self.number,
            self.status
        )


class TravelType(object):
    PROGRAMME_MONITORING = 'Programmatic Visit'
    SPOT_CHECK = 'Spot Check'
    ADVOCACY = 'Advocacy'
    TECHNICAL_SUPPORT = 'Technical Support'
    MEETING = 'Meeting'
    STAFF_DEVELOPMENT = 'Staff Development'
    STAFF_ENTITLEMENT = 'Staff Entitlement'
    CHOICES = (
        (PROGRAMME_MONITORING, 'Programmatic Visit'),
        (SPOT_CHECK, 'Spot Check'),
        (ADVOCACY, 'Advocacy'),
        (TECHNICAL_SUPPORT, 'Technical Support'),
        (MEETING, 'Meeting'),
        (STAFF_DEVELOPMENT, 'Staff Development'),
        (STAFF_ENTITLEMENT, 'Staff Entitlement'),
    )


# TODO: all of these models that only have 1 field should be a choice field on the models that are using it
# for many-to-many array fields are recommended
class ModeOfTravel(object):
    PLANE = 'Plane'
    BUS = 'Bus'
    CAR = 'Car'
    BOAT = 'Boat'
    RAIL = 'Rail'
    CHOICES = (
        (PLANE, 'Plane'),
        (BUS, 'Bus'),
        (CAR, 'Car'),
        (BOAT, 'Boat'),
        (RAIL, 'Rail')
    )


class Travel(models.Model):
    PLANNED = 'planned'
    SUBMITTED = 'submitted'
    REJECTED = 'rejected'
    APPROVED = 'approved'
    CANCELLED = 'cancelled'
    SENT_FOR_PAYMENT = 'sent_for_payment'
    CERTIFICATION_SUBMITTED = 'certification_submitted'
    CERTIFICATION_APPROVED = 'certification_approved'
    CERTIFICATION_REJECTED = 'certification_rejected'
    CERTIFIED = 'certified'
    COMPLETED = 'completed'

    CHOICES = (
        (PLANNED, _('Planned')),
        (SUBMITTED, _('Submitted')),
        (REJECTED, _('Rejected')),
        (APPROVED, _('Approved')),
        (COMPLETED, _('Completed')),
        (CANCELLED, _('Cancelled')),
        (SENT_FOR_PAYMENT, _('Sent for payment')),
        (CERTIFICATION_SUBMITTED, _('Certification submitted')),
        (CERTIFICATION_APPROVED, _('Certification approved')),
        (CERTIFICATION_REJECTED, _('Certification rejected')),
        (CERTIFIED, _('Certified')),
    )

    created = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name=_('Created'))
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Completed At'))
    canceled_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Canceled At'))
    submitted_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Submitted At'))
    # Required to calculate with proper dsa values
    first_submission_date = models.DateTimeField(null=True, blank=True, verbose_name=_('First Submission Date'))
    rejected_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Rejected At'))
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Approved At'))

    rejection_note = models.TextField(default='', blank=True, verbose_name=_('Rejection Note'))
    cancellation_note = models.TextField(default='', blank=True, verbose_name=_('Cancellation Note'))
    certification_note = models.TextField(default='', blank=True, verbose_name=_('Certification Note'))
    report_note = models.TextField(default='', blank=True, verbose_name=_('Report Note'))
    misc_expenses = models.TextField(default='', blank=True, verbose_name=_('Misc Expenses'))

    status = models.CharField(max_length=500, default=PLANNED, verbose_name=_('Status'))
    traveler = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, related_name='travels',
        verbose_name=_('Travellert'),
        on_delete=models.CASCADE,
    )
    traveler_name = models.CharField(max_length=500, blank=True, null=True)
    supervisor = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, related_name='+',
        verbose_name=_('Supervisor'),
        on_delete=models.CASCADE,
    )
    supervisor_name = models.CharField(max_length=500, blank=True, null=True)
    section = models.ForeignKey(
        'users.Section', null=True, blank=True, related_name='+',
        on_delete=models.CASCADE,
    )
    office = models.ForeignKey(
        'users.Office', null=True, blank=True, related_name='+',
        on_delete=models.CASCADE,
    )
    start_date = models.DateField(null=True, blank=True, verbose_name=_('Start Date'))
    end_date = models.DateField(null=True, blank=True, verbose_name=_('End Date'))
    purpose = models.CharField(max_length=500, default='', blank=True, verbose_name=_('Purpose'))
    additional_note = models.TextField(default='', blank=True, verbose_name=_('Additional Note'))
    international_travel = models.NullBooleanField(default=False, null=True, blank=True,
                                                   verbose_name=_('International Travel'))
    ta_required = models.NullBooleanField(default=True, null=True, blank=True, verbose_name=_('TA Required'))
    reference_number = models.CharField(max_length=12, verbose_name=_('Reference Number'))
    hidden = models.BooleanField(default=False, verbose_name=_('Hidden'))
    mode_of_travel = ArrayField(models.CharField(max_length=5, choices=ModeOfTravel.CHOICES), null=True, blank=True,
                                verbose_name=_('Mode of Travel'))
    estimated_travel_cost = models.DecimalField(max_digits=20, decimal_places=4, default=0,
                                                verbose_name=_('Estimated Travel Cost'))

    is_driver = models.BooleanField(default=False, verbose_name=_('Is Driver'))

    # When the travel is sent for payment, the expenses should be saved for later use
    preserved_expenses_local = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True, default=None,
                                                   verbose_name=_('Preserved Expenses (Local)'))
    preserved_expenses_usd = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True, default=None,
                                                 verbose_name=_('Preserved Expenses (USD)'))
    approved_cost_traveler = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True, default=None,
                                                 verbose_name=_('Approved Cost Traveler'))
    approved_cost_travel_agencies = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True,
                                                        default=None, verbose_name=_('Approved Cost Travel Agencies'))

    itinerary_set = ArrayField(models.CharField(max_length=10000), blank=True, null=True)
    activities_set = ArrayField(models.CharField(max_length=10000), blank=True, null=True)
    # activities_set
    attachments_set = ArrayField(models.CharField(max_length=10000), blank=True, null=True)
    attachments_sets = JSONField(blank=True, null=True)
    have_hact = models.IntegerField(blank=True, null=True)
    travel_type = models.CharField(max_length=64, blank=True,
                                   default=TravelType.PROGRAMME_MONITORING,
                                   verbose_name=_('Travel Type'))

    def __str__(self):
        return self.reference_number


class TravelActivity(models.Model):
    travels = models.ManyToManyField('Travel', related_name='activities', verbose_name=_('Travels'))
    travel = models.ForeignKey('Travel', related_name='travels', blank=True, null=True, verbose_name=_('Travels'))
    travel_type = models.CharField(max_length=64, blank=True,
                                   default=TravelType.PROGRAMME_MONITORING,
                                   verbose_name=_('Travel Type'))
    partner = models.ForeignKey(
        PartnerOrganization, null=True, blank=True, related_name='travelactivity_set',
        verbose_name=_('Partner'),
        on_delete=models.CASCADE,
    )
    partnership = models.ForeignKey(
        PCA, null=True, blank=True, related_name='travel_activities',
        verbose_name=_('Partnership'),
        on_delete=models.CASCADE,
    )
    locations = models.ManyToManyField('locations.Location', related_name='+', verbose_name=_('Locations'))
    primary_traveler = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name=_('Primary Traveler'), on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField(null=True, blank=True, verbose_name=_('Date'))
    is_primary_traveler = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = _("Travel Activities")

    @property
    def task_number(self):
        return list(self.travel.activities.values_list('id', flat=True)).index(self.id) + 1

    @property
    def travel_status(self):
        return self.travel.status

    _reference_number = None

    def get_reference_number(self):
        if self._reference_number:
            return self._reference_number

        travel = self.travels.filter(traveler=self.primary_traveler).first()
        if not travel:
            return

        return travel.reference_number

    def set_reference_number(self, value):
        self._reference_number = value

    reference_number = property(get_reference_number, set_reference_number)

    def get_object_url(self):
        travel = self.travels.filter(traveler=self.primary_traveler).first()
        if not travel:
            return

        return travel.get_object_url()

    def __str__(self):
        return '{} - {}'.format(self.travel.reference_number, self.date)


class ItineraryItem(models.Model):
    travel = models.ForeignKey(
        'Travel', related_name='itinerary', verbose_name=_('Travel'),
        on_delete=models.CASCADE,
    )
    origin = models.CharField(max_length=255, verbose_name=_('Origin'))
    destination = models.CharField(max_length=255, verbose_name=_('Destination'))
    departure_date = models.DateTimeField(verbose_name=_('Departure Date'))
    arrival_date = models.DateTimeField(verbose_name=_('Arrival Date'))
    overnight_travel = models.BooleanField(default=False, verbose_name=_('Overnight Travel'))
    mode_of_travel = models.CharField(max_length=5, choices=ModeOfTravel.CHOICES, default='', blank=True,
                                      verbose_name=_('Mode of Travel'))

    class Meta:
        # https://docs.djangoproject.com/en/1.9/ref/models/options/#order-with-respect-to
        # see also
        # https://groups.google.com/d/msg/django-users/NQO8OjCHhnA/r9qKklm5y0EJ
        order_with_respect_to = 'travel'

    def __str__(self):
        return '{} {} - {}'.format(self.travel.reference_number, self.origin, self.destination)


def determine_file_upload_path(instance, filename):
    # TODO: add business area in there
    country_name = connection.schema_name or 'Uncategorized'
    return 'travels/{}/{}/{}'.format(country_name, instance.travel.id, filename)


class TravelAttachment(models.Model):
    travel = models.ForeignKey(
        'Travel', related_name='attachments', verbose_name=_('Travel'),
        on_delete=models.CASCADE,
    )
    type = models.CharField(max_length=64, verbose_name=_('Type'))

    name = models.CharField(max_length=255, verbose_name=_('Name'))
    file = models.FileField(upload_to=determine_file_upload_path, max_length=255, verbose_name=_('File'))


class Engagement(models.Model):
    TYPE_AUDIT = 'audit'
    TYPE_MICRO_ASSESSMENT = 'ma'
    TYPE_SPOT_CHECK = 'sc'
    TYPE_SPECIAL_AUDIT = 'sa'

    TYPES = Choices(
        (TYPE_AUDIT, _('Audit')),
        (TYPE_MICRO_ASSESSMENT, _('Micro Assessment')),
        (TYPE_SPOT_CHECK, _('Spot Check')),
        (TYPE_SPECIAL_AUDIT, _('Special Audit')),
    )

    PARTNER_CONTACTED = 'partner_contacted'
    REPORT_SUBMITTED = 'report_submitted'
    FINAL = 'final'
    CANCELLED = 'cancelled'

    STATUSES = Choices(
        (PARTNER_CONTACTED, _('IP Contacted')),
        (REPORT_SUBMITTED, _('Report Submitted')),
        (FINAL, _('Final Report')),
        (CANCELLED, _('Cancelled')),
    )

    DISPLAY_STATUSES = Choices(
        ('partner_contacted', _('IP Contacted')),
        ('field_visit', _('Field Visit')),
        ('draft_issued_to_partner', _('Draft Report Issued to IP')),
        ('comments_received_by_partner', _('Comments Received from IP')),
        ('draft_issued_to_unicef', _('Draft Report Issued to UNICEF')),
        ('comments_received_by_unicef', _('Comments Received from UNICEF')),
        ('report_submitted', _('Report Submitted')),
        ('final', _('Final Report')),
        ('cancelled', _('Cancelled')),
    )
    DISPLAY_STATUSES_DATES = {
        DISPLAY_STATUSES.partner_contacted: 'partner_contacted_at',
        DISPLAY_STATUSES.field_visit: 'date_of_field_visit',
        DISPLAY_STATUSES.draft_issued_to_partner: 'date_of_draft_report_to_ip',
        DISPLAY_STATUSES.comments_received_by_partner: 'date_of_comments_by_ip',
        DISPLAY_STATUSES.draft_issued_to_unicef: 'date_of_draft_report_to_unicef',
        DISPLAY_STATUSES.comments_received_by_unicef: 'date_of_comments_by_unicef',
        DISPLAY_STATUSES.report_submitted: 'date_of_report_submit',
        DISPLAY_STATUSES.final: 'date_of_final_report',
        DISPLAY_STATUSES.cancelled: 'date_of_cancel'
    }

    OPTION_UNQUALIFIED = "unqualified"
    OPTION_QUALIFIED = "qualified"
    OPTION_DENIAL = "disclaimer_opinion"
    OPTION_ADVERSE = "adverse_opinion"

    OPTIONS = Choices(
        (OPTION_UNQUALIFIED, _("Unqualified")),
        (OPTION_QUALIFIED, _("Qualified")),
        (OPTION_DENIAL, _("Disclaimer opinion")),
        (OPTION_ADVERSE, _("Adverse opinion")),
    )

    unique_id = models.CharField(
        max_length=255,
        blank=True, null=True
    )
    displayed_name = models.CharField(
        max_length=500,
        blank=True, null=True
    )

    status = models.CharField(verbose_name=_('Status'),
                              max_length=30, choices=STATUSES,
                              default=STATUSES.partner_contacted)

    agreement = JSONField(blank=True, null=True)
    po_item = JSONField(blank=True, null=True)
    # auditor - partner organization from agreement
    # agreement = models.ForeignKey(
    #     PurchaseOrder, verbose_name=_('Purchase Order'),
    #     on_delete=models.CASCADE,
    # )
    # po_item = models.ForeignKey(
    #     PurchaseOrderItem, verbose_name=_('PO Item Number'), null=True, blank=True,
    #     on_delete=models.CASCADE,
    # )

    partner = models.ForeignKey(
        PartnerOrganization, verbose_name=_('Partner'),
        on_delete=models.CASCADE,
        blank=True, null=True,
        related_name='engagement_set'
    )
    partner_contacted_at = models.DateField(verbose_name=_('Date IP was contacted'), blank=True, null=True)
    engagement_type = models.CharField(verbose_name=_('Engagement Type'), max_length=10, choices=TYPES)
    start_date = models.DateField(verbose_name=_('Period Start Date'), blank=True, null=True)
    end_date = models.DateField(verbose_name=_('Period End Date'), blank=True, null=True)
    total_value = models.DecimalField(
        verbose_name=_('Total value of selected FACE form(s)'), blank=True, default=0, decimal_places=2, max_digits=20
    )
    exchange_rate = models.DecimalField(
        verbose_name=_('Exchange Rate'), blank=True, default=0, decimal_places=2, max_digits=20
    )

    engagement_attachments = models.CharField(max_length=250, blank=True, null=True)
    report_attachments = models.CharField(max_length=250, blank=True, null=True)

    date_of_field_visit = models.DateField(verbose_name=_('Date of Field Visit'), null=True, blank=True)
    date_of_draft_report_to_ip = models.DateField(
        verbose_name=_('Date Draft Report Issued to IP'), null=True, blank=True
    )
    date_of_comments_by_ip = models.DateField(
        verbose_name=_('Date Comments Received from IP'), null=True, blank=True
    )
    date_of_draft_report_to_unicef = models.DateField(
        verbose_name=_('Date Draft Report Issued to UNICEF'), null=True, blank=True
    )
    date_of_comments_by_unicef = models.DateField(
        verbose_name=_('Date Comments Received from UNICEF'), null=True, blank=True
    )

    date_of_report_submit = models.DateField(verbose_name=_('Date Report Submitted'), null=True, blank=True)
    date_of_final_report = models.DateField(verbose_name=_('Date Report Finalized'), null=True, blank=True)
    date_of_cancel = models.DateField(verbose_name=_('Date Report Cancelled'), null=True, blank=True)

    amount_refunded = models.DecimalField(
        verbose_name=_('Amount Refunded'), blank=True, default=0, decimal_places=2, max_digits=20
    )
    additional_supporting_documentation_provided = models.DecimalField(
        verbose_name=_('Additional Supporting Documentation Provided'), blank=True, default=0,
        decimal_places=2, max_digits=20
    )
    justification_provided_and_accepted = models.DecimalField(
        verbose_name=_('Justification Provided and Accepted'), blank=True, default=0, decimal_places=2, max_digits=20
    )
    write_off_required = models.DecimalField(
        verbose_name=_('Impairment'), blank=True, default=0, decimal_places=2, max_digits=20
    )
    explanation_for_additional_information = models.TextField(
        verbose_name=_('Provide explanation for additional information received from the IP or add attachments'),
        blank=True
    )

    joint_audit = models.BooleanField(verbose_name=_('Joint Audit'), default=False, blank=True)
    shared_ip_with = ArrayField(models.CharField(
        max_length=20, choices=PartnerOrganization.AGENCY_CHOICES
    ), blank=True, default=list, verbose_name=_('Shared Audit with'))

    staff_members = ArrayField(models.CharField(max_length=2500), blank=True, null=True)
    # staff_members = models.ManyToManyField(AuditorStaffMember, verbose_name=_('Staff Members'))

    cancel_comment = models.TextField(blank=True, verbose_name=_('Cancel Comment'))

    active_pd = models.ManyToManyField(PCA, verbose_name=_('Active PDs'))

    authorized_officers = ArrayField(models.CharField(max_length=2500), blank=True, null=True)

    total_amount_tested = models.DecimalField(verbose_name=_('Total Amount Tested'), blank=True, default=0,
                                              decimal_places=2, max_digits=20)
    total_amount_of_ineligible_expenditure = models.DecimalField(
        verbose_name=_('Total Amount of Ineligible Expenditure'), default=0, blank=True,
        decimal_places=2, max_digits=20,
    )

    internal_controls = models.TextField(verbose_name=_('Internal Controls'), blank=True)

    final_report = models.CharField(max_length=250, blank=True, null=True)

    audited_expenditure = models.DecimalField(verbose_name=_('Audited Expenditure $'), blank=True, default=0,
                                              decimal_places=2, max_digits=20)
    financial_findings = models.DecimalField(verbose_name=_('Financial Findings $'), blank=True, default=0,
                                             decimal_places=2, max_digits=20)
    audit_opinion = models.CharField(
        verbose_name=_('Audit Opinion'), max_length=20, choices=OPTIONS, default='', blank=True,
    )

    description = models.TextField()

    finding = models.TextField(blank=True)

    pending_unsupported_amount = models.CharField(max_length=250, blank=True, null=True)

    findings = ArrayField(models.CharField(max_length=10000), blank=True, null=True)
    findings_sets = JSONField(blank=True, null=True)

    class Meta:
        ordering = ('id',)
        verbose_name = _('Engagement')
        verbose_name_plural = _('Engagements')

    # @property
    # def findings_sets(self):
    #     data = []
    #     for item in self.findings:
    #         print(type(item))
    #         data.append(json.dumps(item))
    #
    #     return data

    @property
    def displayed_status(self):
        if self.status != self.STATUSES.partner_contacted:
            return self.status

        if self.date_of_comments_by_unicef:
            return self.DISPLAY_STATUSES.comments_received_by_unicef
        elif self.date_of_draft_report_to_unicef:
            return self.DISPLAY_STATUSES.draft_issued_to_unicef
        elif self.date_of_comments_by_ip:
            return self.DISPLAY_STATUSES.comments_received_by_partner
        elif self.date_of_draft_report_to_ip:
            return self.DISPLAY_STATUSES.draft_issued_to_partner
        elif self.date_of_field_visit:
            return self.DISPLAY_STATUSES.field_visit

        return self.status

    @property
    def displayed_status_date(self):
        return getattr(self, self.DISPLAY_STATUSES_DATES[self.displayed_status])

    def get_shared_ip_with_display(self):
        return list(map(lambda po: dict(PartnerOrganization.AGENCY_CHOICES).get(po, 'Unknown'), self.shared_ip_with))

    @property
    def reference_number(self):
        return self.unique_id

    def __str__(self):
        return '{} on: {} {}'.format(
            self.DISPLAY_STATUSES[self.displayed_status],
            self.displayed_status_date,
            self.reference_number
        )

    def save(self, **kwargs):
        self.displayed_name = '{} on: {} {}'.format(
            self.DISPLAY_STATUSES[self.displayed_status],
            self.displayed_status_date,
            self.reference_number
        )
        super(Engagement, self).save(**kwargs)


class Finding(models.Model):
    PRIORITIES = Choices(
        ('high', _('High')),
        ('low', _('Low')),
    )

    CATEGORIES = Choices(
        ("expenditure_not_for_programme_purposes", _("Expenditure not for programme purposes")),
        ("expenditure_claimed_but_activities_not_undertaken", _("Expenditure claimed but activities not undertaken")),
        ("expenditure_exceeds_the_approved_budget_rate_or_amount",
         _("Expenditure exceeds the approved budget rate or amount")),
        ("expenditure_not_recorded_in_the_correct_period_or_face_form",
         _("Expenditure not recorded in the correct period or FACE form")),
        ("advance_claimed_as_expenditure", _("Advance claimed as expenditure")),
        ("commitments_treated_as_expenditure", _("Commitments treated as expenditure")),
        ("signatories_on_face_forms_different_from_ip_agreement",
         _("Signatories on FACE forms different from those in the IP Agreement")),
        ("no_supporting_documentation", _("No supporting documentation")),
        ("insufficient_supporting_documentation", _("Insufficient supporting documentation")),
        ("no_proof_of_payment", _("No proof of payment")),
        ("no_proof_of_goods_received", _("No proof of goods / services received")),
        ("poor_record_keeping", _("Poor record keeping")),
        ("lack_of_audit_trail",
         _("Lack of audit trail (FACE forms do not reconcile with IPs and UNICEF's accounting records)")),
        ("lack_of_bank_reconciliations", _("Lack of bank reconciliations")),
        ("lack_of_segregation_of_duties", _("Lack of segregation of duties")),
        ("vat_incorrectly_claimed", _("VAT incorrectly claimed")),
        ("ineligible_salary_cost", _("Ineligible salary cost")),
        ("dsa_rates_exceeded", _("DSA rates exceeded")),
        ("support_costs_incorrectly_calculated", _("Support costs incorrectly calculated")),
        ("no_competitive_procedures_for_the_award_of_contracts",
         _("No competitive procedures for the award of contracts")),
        ("suppliers_invoices_not_approved", _("Supplier's invoices not approved")),
        ("no_evaluation_of_goods_received", _("No evaluation of goods received")),
        ("lack_of_procedures_for_verification_of_assets", _("Lack of procedures for verification of assets")),
        ("goods_/_assets_not_used_for_the_intended_purposes", _("Goods / Assets not used for the intended purposes")),
        ("lack_of_written_agreement_between_ip_and_sub-contractee",
         _("Lack of written agreement between IP and sub-contractee")),
        ("lack_of_sub-contractee_financial",
         _("Lack of sub-contractee financial / substantive progress reporting on file")),
        ("failure_to_implement_prior_assurance_activity_recommendations",
         _("Failure to implement prior assurance activity recommendations")),
        ("other", _("Other")),
    )

    spot_check = models.ForeignKey(
        Engagement, verbose_name=_('Spot Check'), related_name='+',
        on_delete=models.CASCADE,
    )

    priority = models.CharField(verbose_name=_('Priority'), max_length=4, choices=PRIORITIES)

    category_of_observation = models.CharField(
        verbose_name=_('Category of Observation'), max_length=100, choices=CATEGORIES,
    )
    recommendation = models.TextField(verbose_name=_('Finding and Recommendation'), blank=True)
    agreed_action_by_ip = models.TextField(verbose_name=_('Agreed Action by IP'), blank=True)
    deadline_of_action = models.DateField(verbose_name=_('Deadline of Action'), null=True, blank=True)

    class Meta:
        ordering = ('id', )
        verbose_name = _('Finding')
        verbose_name_plural = _('Findings')

    def __str__(self):
        return 'Finding for {}'.format(self.spot_check)


class DetailedFindingInfo(models.Model):
    finding = models.TextField(verbose_name=_('Description of Finding'))
    recommendation = models.TextField(verbose_name=_('Recommendation and IP Management Response'))

    micro_assesment = models.ForeignKey(
        Engagement, verbose_name=_('Micro Assessment'), related_name='+',
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ('id', )
        verbose_name = _('Detailed Finding Info')
        verbose_name_plural = _('Detailed Findings Info')

    def __str__(self):
        return 'Finding for {}'.format(self.micro_assesment)


class FinancialFinding(models.Model):
    TITLE_CHOICES = Choices(
        ('no-supporting-documentation', _('No supporting documentation')),
        ('insufficient-supporting-documentation', _('Insufficient supporting documentation')),
        ('cut-off-error', _('Cut-off error')),
        ('expenditure-not-for-project-purposes', _('Expenditure not for project purposes')),
        ('no-proof-of-payment', _('No proof of payment')),
        ('no-proof-of-goods-services-received', _('No proof of goods / services received')),
        ('vat-incorrectly-claimed', _('VAT incorrectly claimed')),
        ('dsa-rates-exceeded', _('DSA rates exceeded')),
        ('unreasonable-price', _('Unreasonable price')),
        ('bank-interest-not-reported', _('Bank interest not reported')),
        ('support-costs-incorrectly-calculated', _('Support costs incorrectly calculated')),
        ('expenditure-claimed-but-activities-not-undertaken', _('Expenditure claimed but activities not undertaken')),
        ('advance-claimed-as-expenditure', _('Advance claimed as expenditure')),
        ('commitments-treated-as-expenditure', _('Commitments treated as expenditure')),
        ('ineligible-salary-costs', _('Ineligible salary costs')),
        ('ineligible-costs-other', _('Ineligible costs (other)')),
    )

    audit = models.ForeignKey(
        Engagement, verbose_name=_('Audit'), related_name='+',
        on_delete=models.CASCADE,
    )

    title = models.CharField(verbose_name=_('Title (Category)'), max_length=255, choices=TITLE_CHOICES)
    local_amount = models.DecimalField(verbose_name=_('Amount (local)'), decimal_places=2, max_digits=20)
    amount = models.DecimalField(verbose_name=_('Amount (USD)'), decimal_places=2, max_digits=20)
    description = models.TextField(verbose_name=_('Description'))
    recommendation = models.TextField(verbose_name=_('Recommendation'), blank=True)
    ip_comments = models.TextField(verbose_name=_('IP Comments'), blank=True)

    class Meta:
        ordering = ('id', )

    def __str__(self):
        return '{}: {}'.format(self.audit.unique_id, self.get_title_display())


class Category(OrderedModel, TimeStampedModel):
    MODULE_CHOICES = Choices(
        ('apd', _('Action Points')),
        ('t2f', _('Trip Management')),
        ('tpm', _('Third Party Monitoring')),
        ('audit', _('Financial Assurance')),
    )

    module = models.CharField(max_length=10, choices=MODULE_CHOICES, verbose_name=_('Module'))
    description = models.TextField(verbose_name=_('Description'))

    class Meta:
        unique_together = ("description", "module", )
        ordering = ('module', 'order')
        verbose_name = _('Action point category')
        verbose_name_plural = _('Action point categories')

    def __str__(self):
        return '{}: {}'.format(self.module, self.description)


class ActionPoint(TimeStampedModel):
    MODULE_CHOICES = Category.MODULE_CHOICES

    STATUS_OPEN = 'open'
    STATUS_COMPLETED = 'completed'

    STATUSES = Choices(
        (STATUS_OPEN, _('Open')),
        (STATUS_COMPLETED, _('Completed')),
    )

    STATUSES_DATES = {
        STATUSES.open: 'created',
        STATUSES.completed: 'date_of_completion'
    }

    KEY_EVENTS = Choices(
        ('status_update', _('Status Update')),
        ('reassign', _('Reassign')),
    )

    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='created_action_points',
                               verbose_name=_('Author'),
                               on_delete=models.CASCADE, blank=True, null=True)
    author_name = models.CharField(max_length=250, blank=True, null=True)

    assigned_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='+', verbose_name=_('Assigned By'),
                                    on_delete=models.CASCADE, blank=True, null=True)
    assigned_by_name = models.CharField(max_length=250, blank=True, null=True)

    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='assigned_action_points',
                                    verbose_name=_('Assigned To'),
                                    on_delete=models.CASCADE, blank=True, null=True)
    assigned_to_name = models.CharField(max_length=250, blank=True, null=True)

    status = models.CharField(verbose_name=_('Status'), max_length=10, choices=STATUSES, default=STATUSES.open)
    status_date = models.DateTimeField(blank=True, null=True)

    category = models.ForeignKey(Category, verbose_name=_('Category'),
                                 blank=True, null=True, on_delete=models.CASCADE)
    category_name = models.CharField(max_length=1500, blank=True, null=True)

    description = models.TextField(verbose_name=_('Description'))
    due_date = models.DateField(verbose_name=_('Due Date'), blank=True, null=True)
    high_priority = models.BooleanField(default=False, verbose_name=_('High Priority'))

    section = models.ForeignKey('users.Section', verbose_name=_('Section'), blank=True, null=True,
                                on_delete=models.CASCADE)
    office = models.ForeignKey('users.Office', verbose_name=_('Office'), blank=True, null=True,
                               on_delete=models.CASCADE)

    location = models.ForeignKey('locations.Location', verbose_name=_('Location'), blank=True, null=True,
                                 on_delete=models.CASCADE)
    partner = models.ForeignKey(PartnerOrganization, verbose_name=_('Partner'), blank=True, null=True,
                                on_delete=models.CASCADE)
    # cp_output = models.ForeignKey('reports.Result', verbose_name=_('CP Output'), blank=True, null=True,
    #                               on_delete=models.CASCADE)
    intervention = models.ForeignKey(PCA, verbose_name=_('PD/SSFA'), blank=True, null=True,
                                     on_delete=models.CASCADE)
    engagement = models.ForeignKey(Engagement, verbose_name=_('Engagement'), blank=True, null=True,
                                   related_name='action_points', on_delete=models.CASCADE)
    # tpm_activity = models.ForeignKey('tpm.TPMActivity', verbose_name=_('TPM Activity'), blank=True, null=True,
    #                                  related_name='action_points', on_delete=models.CASCADE)
    travel_activity = models.ForeignKey(TravelActivity, verbose_name=_('Travel'), blank=True, null=True,
                                        on_delete=models.CASCADE)
    date_of_completion = models.DateTimeField(blank=True, null=True)
    related_module = models.CharField(max_length=250, blank=True, null=True)
    reference_number = models.CharField(max_length=250, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ('id', )
        verbose_name = _('Action Point')
        verbose_name_plural = _('Action Points')

    @property
    def engagement_subclass(self):
        return self.engagement.get_subclass() if self.engagement else None

    def __str__(self):
        return self.reference_number


class DonorFunding(models.Model):

    donor = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )
    grant = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    total_contribution = models.FloatField(blank=True, null=True)
    programmable = models.FloatField(blank=True, null=True)
    section = models.ForeignKey(
        'users.Section', null=True, blank=True, related_name='+'
    )
    total = models.FloatField(blank=True, null=True)
    comment = models.CharField(
        max_length=1500,
        blank=True,
        null=True
    )
