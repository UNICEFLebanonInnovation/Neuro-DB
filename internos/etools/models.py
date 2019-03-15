from __future__ import unicode_literals

import logging
import datetime
import json
from model_utils.choices import Choices
from django.conf import settings
from django.contrib.postgres.fields.array import ArrayField
from django.db import connection, models
from django.utils.translation import ugettext, ugettext_lazy as _
from django_fsm import FSMField, transition

log = logging.getLogger(__name__)


class PartnerOrganization(models.Model):

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

    @property
    def interventions_details(self):
        data = []
        now = datetime.datetime.now()

        for item in self.interventions.filter(end__year=now.year).order_by('start'):
            data.append({
                'etl_id': item.etl_id,
                'number': item.number,
                'start': item.start,
                'end': item.end,
                'document_type': item.document_type,
                'total_unicef_budget': item.total_unicef_budget,
                'budget_currency': item.budget_currency,
                'total_budget': item.total_budget,
                'offices_names': item.offices_names,
                'location_p_codes': item.location_p_codes
            })
        return data

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
    offices = ArrayField(models.CharField(max_length=200), blank=True, null=True)
    cp_outputs = ArrayField(models.CharField(max_length=200), blank=True, null=True)
    planned_budget = ArrayField(models.CharField(max_length=200), blank=True, null=True)
    amendments = ArrayField(models.CharField(max_length=200), blank=True, null=True)
    result_links = ArrayField(models.CharField(max_length=200), blank=True, null=True)
    location_names = ArrayField(models.CharField(max_length=200), blank=True, null=True)
    planned_visits_list = ArrayField(models.CharField(max_length=200), blank=True, null=True)

    class Meta:
        verbose_name = 'Intervention'
        verbose_name_plural = 'Interventions'
        ordering = ['-created_at']

    def __unicode__(self):
        return u'{}: {}'.format(
            self.partner_name,
            self.number
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
        (COMPLETED, _('Completed')),
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

    status = FSMField(default=PLANNED, choices=CHOICES, protected=True, verbose_name=_('Status'))
    traveler = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, related_name='travels',
        verbose_name=_('Travellert'),
        on_delete=models.CASCADE,
    )
    supervisor = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, related_name='+',
        verbose_name=_('Supervisor'),
        on_delete=models.CASCADE,
    )
    section = models.ForeignKey(
        'users.Section', null=True, blank=True, related_name='+', verbose_name=_('Section'),
        on_delete=models.CASCADE,
    )
    start_date = models.DateTimeField(null=True, blank=True, verbose_name=_('Start Date'))
    end_date = models.DateTimeField(null=True, blank=True, verbose_name=_('End Date'))
    purpose = models.CharField(max_length=500, default='', blank=True, verbose_name=_('Purpose'))
    additional_note = models.TextField(default='', blank=True, verbose_name=_('Additional Note'))
    international_travel = models.NullBooleanField(default=False, null=True, blank=True,
                                                   verbose_name=_('International Travel'))
    ta_required = models.NullBooleanField(default=True, null=True, blank=True, verbose_name=_('TA Required'))
    reference_number = models.CharField(max_length=12, unique=True,
                                        verbose_name=_('Reference Number'))
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

    def __str__(self):
        return self.reference_number


class TravelActivity(models.Model):
    travels = models.ManyToManyField('Travel', related_name='activities', verbose_name=_('Travels'))
    travel_type = models.CharField(max_length=64, choices=TravelType.CHOICES, blank=True,
                                   default=TravelType.PROGRAMME_MONITORING,
                                   verbose_name=_('Travel Type'))
    partner = models.ForeignKey(
        PartnerOrganization, null=True, blank=True, related_name='+',
        verbose_name=_('Partner'),
        on_delete=models.CASCADE,
    )
    # Partnership has to be filtered based on partner
    # TODO: assert self.partnership.agreement.partner == self.partner
    partnership = models.ForeignKey(
        PCA, null=True, blank=True, related_name='travel_activities',
        verbose_name=_('Partnership'),
        on_delete=models.CASCADE,
    )
    locations = models.ManyToManyField('locations.Location', related_name='+', verbose_name=_('Locations'))
    primary_traveler = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name=_('Primary Traveler'), on_delete=models.CASCADE)
    date = models.DateTimeField(null=True, blank=True, verbose_name=_('Date'))

    class Meta:
        verbose_name_plural = _("Travel Activities")

    @property
    def travel(self):
        return self.travels.filter(traveler=self.primary_traveler).first()

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
        return '{} - {}'.format(self.travel_type, self.date)


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
