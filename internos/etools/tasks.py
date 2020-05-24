from internos.taskapp.celery import app

import json
import pytz
import httplib
import datetime
from django.utils import timezone
from time import mktime
from internos.backends.utils import get_data
from internos.backends.models import ImportLog


@app.task
def sync_partner_data():
    from internos.etools.models import PartnerOrganization

    log = ImportLog.start(name='eTools: Sync Partners data')

    partners = get_data('etools.unicef.org', '/api/v2/partners/', 'Token 36f06547a4b930c6608e503db49f1e45305351c2')
    partners = json.loads(partners)
    for item in partners:
        partner, new_instance = PartnerOrganization.objects.get_or_create(etl_id=item['id'])

        partner.rating = item['rating']
        partner.last_assessment_date = item['last_assessment_date']
        partner.short_name = item['short_name']
        partner.postal_code = item['postal_code']
        partner.basis_for_risk_rating = item['basis_for_risk_rating']
        partner.city = item['city']
        partner.reported_cy = item['reported_cy']
        partner.total_ct_ytd = item['total_ct_ytd']
        partner.vendor_number = item['vendor_number']
        partner.hidden = item['hidden']
        partner.cso_type = item['cso_type']
        partner.net_ct_cy = item['net_ct_cy']
        partner.phone_number = item['phone_number']
        partner.shared_with = item['shared_with']
        partner.partner_type = item['partner_type']
        partner.address = item['address']
        partner.total_ct_cy = item['total_ct_cy']
        partner.name = item['name']
        partner.total_ct_cp = item['total_ct_cp']
        partner.country = item['country']
        partner.email = item['email']
        partner.deleted_flag = item['deleted_flag']
        partner.street_address = item['street_address']

        partner.save()

    log.end()


@app.task
def sync_individual_partner_data():
    from internos.etools.models import PartnerOrganization

    log = ImportLog.start(name='eTools: Sync Partners individual data')

    partners = PartnerOrganization.objects.all()

    for partner in partners:
        item = get_data('etools.unicef.org', '/api/v2/partners/{}/'.format(partner.etl_id),
                        'Token 36f06547a4b930c6608e503db49f1e45305351c2')

        try:
            item = json.loads(item)

            partner.rating = item['rating']
            partner.last_assessment_date = item['last_assessment_date']
            partner.short_name = item['short_name']
            partner.postal_code = item['postal_code']
            partner.basis_for_risk_rating = item['basis_for_risk_rating']
            partner.city = item['city']
            partner.reported_cy = item['reported_cy']
            partner.total_ct_ytd = item['total_ct_ytd']
            partner.vendor_number = item['vendor_number']
            partner.hidden = item['hidden']
            partner.cso_type = item['cso_type']
            partner.net_ct_cy = item['net_ct_cy']
            partner.phone_number = item['phone_number']
            partner.shared_with = item['shared_with']
            partner.partner_type = item['partner_type']
            partner.address = item['address']
            partner.total_ct_cy = item['total_ct_cy']
            partner.name = item['name']
            partner.total_ct_cp = item['total_ct_cp']
            partner.country = item['country']
            partner.email = item['email']
            partner.deleted_flag = item['deleted_flag']
            partner.street_address = item['street_address']

            partner.staff_members = item['staff_members']
            partner.assessments = item['assessments']
            partner.planned_engagement = item['planned_engagement']
            partner.hact_values = item['hact_values']
            partner.hact_min_requirements = item['hact_min_requirements']
            partner.planned_visits = item['planned_visits']
            partner.core_values_assessments = item['core_values_assessments']
            partner.flags = item['flags']
            partner.type_of_assessment = item['type_of_assessment']

            if item['last_assessment_date']:
                partner.last_assessment_date = datetime.datetime.strptime(item['last_assessment_date'], "%Y-%m-%d")

            if item['core_values_assessment_date']:
                partner.core_values_assessment_date = datetime.datetime.strptime(item['core_values_assessment_date'], "%Y-%m-%d")

            partner.total_ct_cp = item['total_ct_cp']
            partner.total_ct_cy = item['total_ct_cy']
            partner.net_ct_cy = item['net_ct_cy']
            partner.reported_cy = item['reported_cy']
            partner.total_ct_ytd = item['total_ct_ytd']

            partner.save()
        except Exception as ex:
            print(item)
            print(ex.message)
            continue

    log.end()


@app.task
def sync_agreement_data():
    from internos.etools.models import Agreement, PartnerOrganization
    log = ImportLog.start(name='eTools: Sync PCA data')

    result = get_data('etools.unicef.org', '/api/v2/agreements/', 'Token 36f06547a4b930c6608e503db49f1e45305351c2')

    result = json.loads(result)
    for item in result:
        instance, create = Agreement.objects.get_or_create(etl_id=item['id'])

        instance.partner = PartnerOrganization.objects.get(etl_id=item['partner'])
        instance.country_programme = item['country_programme']
        instance.agreement_number = item['agreement_number']
        instance.partner_name = item['partner_name']
        instance.agreement_type = item['agreement_type']
        instance.end = item['end']
        instance.start = item['start']
        instance.signed_by_unicef_date = item['signed_by_unicef_date']
        instance.signed_by_partner_date = item['signed_by_partner_date']
        instance.status = item['status']
        instance.agreement_number_status = item['agreement_number_status']
        instance.special_conditions_pca = item['special_conditions_pca']

        instance.save()

    log.end()


@app.task
def sync_intervention_data():
    from internos.etools.models import PCA
    from internos.locations.models import Location

    log = ImportLog.start(name='eTools: Sync PD data')

    result = get_data('etools.unicef.org', '/api/v2/interventions/', 'Token 36f06547a4b930c6608e503db49f1e45305351c2')

    result = json.loads(result)
    for item in result:
        instance, create = PCA.objects.get_or_create(etl_id=item['id'])

        instance.number = item['number']
        instance.document_type = item['document_type']
        instance.partner_name = item['partner_name']
        instance.status = item['status']
        instance.title = item['title']
        instance.start = item['start']
        instance.end = item['end']
        instance.end_date = item['end']
        instance.frs_total_frs_amt = item['frs_total_frs_amt']
        instance.unicef_cash = item['unicef_cash']
        instance.cso_contribution = item['cso_contribution']
        instance.country_programme = item['country_programme']
        instance.frs_earliest_start_date = item['frs_earliest_start_date']
        instance.frs_latest_end_date = item['frs_latest_end_date']
        instance.sections = item['sections']
        instance.section_names = item['section_names']
        instance.cp_outputs = item['cp_outputs']
        instance.unicef_focal_points = item['unicef_focal_points']
        instance.frs_total_intervention_amt = item['frs_total_intervention_amt']
        instance.frs_total_outstanding_amt = item['frs_total_outstanding_amt']
        instance.offices = item['offices']
        instance.actual_amount = item['actual_amount']
        instance.offices_names = item['offices_names']
        instance.total_unicef_budget = item['total_unicef_budget']
        instance.total_budget = item['total_budget']
        instance.metadata = item['metadata']
        instance.flagged_sections = item['flagged_sections']
        instance.budget_currency = item['budget_currency']
        instance.fr_currencies_are_consistent = item['fr_currencies_are_consistent']
        instance.all_currencies_are_consistent = item['all_currencies_are_consistent']
        instance.fr_currency = item['fr_currency']
        instance.multi_curr_flag = item['multi_curr_flag']
        instance.location_p_codes = item['location_p_codes']
        instance.donors = item['donors']
        instance.donor_codes = item['donor_codes']
        instance.grants = item['grants']

        for p_code in item['location_p_codes']:
            try:
                instance.locations.add(Location.objects.filter(p_code=p_code).first())
            except Exception:
                continue

        instance.save()

    log.end()


@app.task
def sync_intervention_individual_data(instance=None):
    from internos.etools.models import PCA, PartnerOrganization, Agreement

    log = ImportLog.start(name='eTools: Sync PD individual data')

    interventions = PCA.objects.filter(donors__len__gt=0)

    for instance in interventions:
        item = get_data('etools.unicef.org', '/api/v2/interventions/'+instance.etl_id+'/',
                        'Token 36f06547a4b930c6608e503db49f1e45305351c2')

        try:
            item = json.loads(item)

            instance.partner = PartnerOrganization.objects.get(etl_id=item['partner_id'])
            instance.agreement = Agreement.objects.get(etl_id=item['agreement'])
            instance.number = item['number']
            instance.document_type = item['document_type']
            instance.status = item['status']
            instance.title = item['title']
            instance.start = item['start']
            instance.end = item['end']
            instance.end_date = item['end']
            instance.frs_details = item['frs_details']

            for fr in item['frs_details']['frs']:
                instance.donors_set = fr['line_item_details']

            instance.save()
        except Exception as ex:
            print(item)
            print(ex.message)
            continue

    log.end()


@app.task
def sync_audit_data():
    from internos.etools.models import Engagement, PartnerOrganization

    log = ImportLog.start(name='eTools: Sync Audit data')

    instances = get_data('etools.unicef.org', '/api/audit/engagements/?page_size=1000', 'Token 36f06547a4b930c6608e503db49f1e45305351c2')
    instances = json.loads(instances)
    for item in instances['results']:

        instance, new_instance = Engagement.objects.get_or_create(id=int(item['id']))

        instance.unique_id = item['unique_id']
        instance.agreement = item['agreement']
        instance.engagement_type = item['engagement_type']
        instance.total_value = item['total_value']
        instance.partner = PartnerOrganization.objects.get(etl_id=item['partner']['id'])
        instance.status = item['status']
        instance.status_date = item['status_date']

        instance.save()
        sync_audit_individual_data(instance)

    log.end()


@app.task
def sync_audit_individual_data(instance):
    from internos.etools.models import PCA

    api_func = '/api/audit/engagement/'
    if instance.engagement_type == instance.TYPE_AUDIT:
        api_func = '/api/audit/audits/{}/'.format(instance.id)

    elif instance.engagement_type == instance.TYPE_MICRO_ASSESSMENT:
        api_func = '/api/audit/micro-assessments/{}/'.format(instance.id)

    elif instance.engagement_type == instance.TYPE_SPOT_CHECK:
        api_func = '/api/audit/spot-checks/{}/'.format(instance.id)

    elif instance.engagement_type == instance.TYPE_SPECIAL_AUDIT:
        api_func = '/api/audit/special-audits/{}/'.format(instance.id)

    data = get_data('etools.unicef.org', api_func, 'Token 36f06547a4b930c6608e503db49f1e45305351c2')
    data = json.loads(data)

    if 'face_form_start_date' in data:
        instance.face_form_start_date = data['face_form_start_date']
    if 'face_form_end_date' in data:
        instance.face_form_end_date = data['face_form_end_date']
    if 'cancel_comment' in data:
        instance.cancel_comment = data['cancel_comment']

    instance.agreement = data['agreement']
    instance.po_item = data['po_item']

    if 'related_agreement' in data:
        instance.related_agreement = data['related_agreement']

    if 'exchange_rate' in data:
        instance.exchange_rate = data['exchange_rate']

    if 'total_amount_tested' in data:
        instance.total_amount_tested = data['total_amount_tested']

    if 'total_amount_of_ineligible_expenditure' in data:
        instance.total_amount_of_ineligible_expenditure = data['total_amount_of_ineligible_expenditure']

    if 'internal_controls' in data:
        instance.internal_controls = data['internal_controls']

    if 'amount_refunded' in data:
        instance.amount_refunded = data['amount_refunded']

    if 'additional_supporting_documentation_provided' in data:
        instance.additional_supporting_documentation_provided = data['additional_supporting_documentation_provided']

    if 'justification_provided_and_accepted' in data:
        instance.justification_provided_and_accepted = data['justification_provided_and_accepted']

    if 'write_off_required' in data:
        instance.write_off_required = data['write_off_required']

    if 'explanation_for_additional_information' in data:
        instance.explanation_for_additional_information = data['explanation_for_additional_information']

    if 'audited_expenditure' in data:
        instance.audited_expenditure = data['audited_expenditure']

    if 'financial_findings' in data:
        instance.financial_findings = data['financial_findings']

    if 'audit_opinion' in data:
        instance.audit_opinion = data['audit_opinion']

    if 'pending_unsupported_amount' in data:
        instance.pending_unsupported_amount = data['pending_unsupported_amount']

    if 'findings' in data:
        instance.findings = data['findings']

    if 'findings' in data:
        instance.findings_sets = data['findings']

    instance.partner_contacted_at = data['partner_contacted_at']
    instance.start_date = data['start_date']
    instance.end_date = data['end_date']
    instance.authorized_officers = data['authorized_officers']
    for pd in data['active_pd']:
        instance.active_pd.add(PCA.objects.get(etl_id=pd['id']))

    instance.staff_members = data['staff_members']

    instance.date_of_cancel = data['date_of_cancel']
    instance.date_of_final_report = data['date_of_final_report']
    instance.date_of_report_submit = data['date_of_report_submit']
    instance.date_of_comments_by_ip = data['date_of_comments_by_ip']
    instance.date_of_comments_by_unicef = data['date_of_comments_by_unicef']
    instance.date_of_draft_report_to_ip = data['date_of_draft_report_to_ip']
    instance.date_of_draft_report_to_unicef = data['date_of_draft_report_to_unicef']
    instance.date_of_field_visit = data['date_of_field_visit']

    if 'joint_audit' in data:
        instance.joint_audit = data['joint_audit']
    if 'shared_ip_with' in data:
        instance.shared_ip_with = data['shared_ip_with']

    instance.save()


@app.task
def sync_trip_data():
    from internos.etools.models import Engagement, PartnerOrganization, Travel

    log = ImportLog.start(name='eTools: Sync Trips data')

    for page in range(320, 500):

        try:
            api_func = '/api/t2f/travels/?page={}&page_size={}'.format(page, 100)
            instances = get_data('etools.unicef.org', api_func, 'Token 36f06547a4b930c6608e503db49f1e45305351c2')
            instances = json.loads(instances)
            for item in instances['data']:

                instance, new_instance = Travel.objects.get_or_create(id=item['id'])

                instance.reference_number = item['reference_number']
                instance.traveler_name = item['traveler']
                instance.purpose = item['purpose']
                instance.status = item['status'].lower()
                instance.start_date = datetime.datetime.strptime(item['start_date'], "%Y-%m-%d") if item['start_date'] else ''
                instance.end_date = datetime.datetime.strptime(item['end_date'], "%Y-%m-%d") if item['end_date'] else ''
                instance.supervisor_name = item['supervisor_name']
                instance.section_id = item['section']
                instance.office_id = item['office']

                instance.save()
        except Exception as ex:
            print(ex.message)
            # print(item)
            continue

    log.end()


@app.task
def sync_trip_individual_data(instance):
    from internos.etools.models import TravelActivity, PartnerOrganization, PCA
    from internos.locations.models import Location
    data = get_data('etools.unicef.org', '/api/t2f/travels/{}/'.format(instance.id),
                    'Token 36f06547a4b930c6608e503db49f1e45305351c2')
    item = json.loads(data)

    instance.international_travel = item['international_travel']
    instance.ta_required = item['ta_required']
    instance.itinerary_set = item['itinerary']
    instance.activities_set = item['activities']
    for activity in item['activities']:
        instance.travel_type = activity['travel_type'].title()
        act_instance, new_instance = TravelActivity.objects.get_or_create(id=activity['id'])

        act_instance.travel_type = activity['travel_type'].title()

        if activity['date']:
            act_instance.date = datetime.datetime.strptime(item['start_date'], "%Y-%m-%d")
        else:
            act_instance.date = instance.start_date

        act_instance.is_primary_traveler = activity['is_primary_traveler']
        act_instance.travel = instance

        if activity['partner']:
            act_instance.partner = PartnerOrganization.objects.get(etl_id=activity['partner'])

        if activity['partnership']:
            act_instance.partnership = PCA.objects.get(etl_id=activity['partnership'])

        locations = activity['locations']
        for location in locations:
            try:
                act_instance.locations.add(Location.objects.filter(id=location).first())
            except Exception:
                continue

        act_instance.save()

    instance.mode_of_travel = item['mode_of_travel']
    instance.estimated_travel_cost = item['estimated_travel_cost']
    instance.completed_at = item['completed_at']
    instance.canceled_at = item['canceled_at']
    instance.rejection_note = item['rejection_note']
    instance.cancellation_note = item['cancellation_note']
    instance.attachments_set = item['attachments']
    instance.attachments_sets = item['attachments']

    instance.have_hact = 0
    for attache in instance.attachments_sets:
        if 'HACT' in attache['name'] and '.docx' in attache['name']:
            instance.have_hact += 1
    instance.certification_note = item['certification_note']
    instance.report = item['report']
    instance.additional_note = item['additional_note']
    instance.misc_expenses = item['misc_expenses']
    instance.first_submission_date = item['first_submission_date']

    instance.save()


@app.task
def sync_action_points_data():
    from internos.etools.models import Engagement, PartnerOrganization, ActionPoint

    log = ImportLog.start(name='eTools: Sync Action points data')

    engagements = Engagement.objects.filter(status=Engagement.FINAL)

    for engagement in engagements.iterator():

        api_func = '/api/action-points/action-points/?engagement={}'.format(engagement.id)

        data = get_data('etools.unicef.org', api_func, 'Token 36f06547a4b930c6608e503db49f1e45305351c2')
        data = json.loads(data)

        for item in data['results']:
            instance, created = ActionPoint.objects.get_or_create(id=int(item['id']))

            instance.reference_number = item['reference_number']
            instance.related_module = '{}_{}'.format(item['related_module'], engagement.engagement_type)
            instance.category_id = int(item['category']['id'])
            instance.category_name = item['category']['description']
            instance.description = item['description']
            instance.due_date = item['due_date']
            instance.author_name = item['author']['name']
            instance.assigned_by_name = item['assigned_by']['name']
            instance.assigned_to_name = item['assigned_to']['name']
            instance.high_priority = item['high_priority']
            instance.section_id = int(item['section']['id'])
            instance.office_id = int(item['office']['id'])
            instance.engagement = engagement
            instance.status = item['status']
            instance.status_date = item['status_date']
            instance.partner_id = PartnerOrganization.objects.get(etl_id=int(item['partner']['id']))

            instance.save()

    log.end()
