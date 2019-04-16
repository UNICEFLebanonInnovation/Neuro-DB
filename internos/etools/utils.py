from internos.taskapp.celery import app

import json
import httplib
import datetime
from time import mktime


def sync_partner_data():
    from internos.etools.models import PartnerOrganization
    partners = get_data('etools.unicef.org', '/api/v2/partners/', 'Token 36f06547a4b930c6608e503db49f1e45305351c2')
    partners = json.loads(partners)
    for item in partners:
        partner, new_instance = PartnerOrganization.objects.get_or_create(etl_id=item['id'])

        # for key in item:
        #     setattr(partner, key, item[key])

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


def sync_agreement_data():
    from internos.etools.models import Agreement, PartnerOrganization
    partners = get_data('etools.unicef.org', '/api/v2/agreements/', 'Token 36f06547a4b930c6608e503db49f1e45305351c2')

    partners = json.loads(partners)
    for item in partners:
        partner, new_instance = Agreement.objects.get_or_create(etl_id=item['id'])

        # for key in item:
        #     setattr(partner, key, item[key])

        partner.partner = PartnerOrganization.objects.get(etl_id=item['partner'])
        partner.country_programme = item['country_programme']
        partner.agreement_number = item['agreement_number']
        partner.partner_name = item['partner_name']
        partner.agreement_type = item['agreement_type']
        partner.end = item['end']
        partner.start = item['start']
        partner.signed_by_unicef_date = item['signed_by_unicef_date']
        partner.signed_by_partner_date = item['signed_by_partner_date']
        partner.status = item['status']
        partner.agreement_number_status = item['agreement_number_status']
        partner.special_conditions_pca = item['special_conditions_pca']

        partner.save()


def sync_intervention_data():
    from internos.etools.models import Agreement, PartnerOrganization, PCA
    partners = get_data('etools.unicef.org', '/api/v2/interventions/', 'Token 36f06547a4b930c6608e503db49f1e45305351c2')

    partners = json.loads(partners)
    for item in partners:
        partner, new_instance = PCA.objects.get_or_create(etl_id=item['id'])

        partner.number = item['number']
        partner.document_type = item['document_type']
        partner.partner_name = item['partner_name']
        partner.status = item['status']
        partner.title = item['title']
        partner.start = item['start']
        partner.end = item['end']
        partner.frs_total_frs_amt = item['frs_total_frs_amt']
        partner.unicef_cash = item['unicef_cash']
        partner.cso_contribution = item['cso_contribution']
        partner.country_programme = item['country_programme']
        partner.frs_earliest_start_date = item['frs_earliest_start_date']
        partner.frs_latest_end_date = item['frs_latest_end_date']
        partner.sections = item['sections']
        partner.section_names = item['section_names']
        partner.cp_outputs = item['cp_outputs']
        partner.unicef_focal_points = item['unicef_focal_points']
        partner.frs_total_intervention_amt = item['frs_total_intervention_amt']
        partner.frs_total_outstanding_amt = item['frs_total_outstanding_amt']
        partner.offices = item['offices']
        partner.actual_amount = item['actual_amount']
        partner.offices_names = item['offices_names']
        partner.total_unicef_budget = item['total_unicef_budget']
        partner.total_budget = item['total_budget']
        partner.metadata = item['metadata']
        partner.flagged_sections = item['flagged_sections']
        partner.budget_currency = item['budget_currency']
        partner.fr_currencies_are_consistent = item['fr_currencies_are_consistent']
        partner.all_currencies_are_consistent = item['all_currencies_are_consistent']
        partner.fr_currency = item['fr_currency']
        partner.multi_curr_flag = item['multi_curr_flag']
        partner.location_p_codes = item['location_p_codes']
        partner.donors = item['donors']
        partner.donor_codes = item['donor_codes']
        partner.grants = item['grants']

        partner.save()
        # update_individual_intervention_data(partner)


def update_individual_intervention_data(partner=None):
    from internos.etools.models import Agreement, PartnerOrganization, PCA
    interventions = PCA.objects.all()

    for partner in interventions:
        item = get_data('etools.unicef.org', '/api/v2/interventions/'+partner.etl_id+'/',
                        'Token 36f06547a4b930c6608e503db49f1e45305351c2')

        item = json.loads(item)
        try:
            partner.partner = PartnerOrganization.objects.get(etl_id=item['partner_id'])
            partner.agreement = Agreement.objects.get(etl_id=item['agreement'])
            partner.number = item['number']
            partner.document_type = item['document_type']
            partner.status = item['status']
            partner.title = item['title']
            partner.start = item['start']
            partner.end = item['end']
            # partner.planned_budget = item['planned_budget']
            # partner.amendments = item['amendments']
            # partner.result_links = item['result_links']
            # partner.planned_visits_list = item['planned_visits']
            # partner.locations = item['locations']
            # partner.location_names = item['location_names']
            # partner.location_p_codes = item['location_p_codes']
            # partner.country_programme = item['country_programme']
            # partner.sections = item['sections']
            # partner.section_names = item['section_names']
            # partner.unicef_focal_points = item['unicef_focal_points']
            # partner.offices = item['offices']
            # partner.flagged_sections = item['flagged_sections']
            # partner.donors = item['donors']
            # partner.donor_codes = item['donor_codes']
            # partner.grants = item['grants']
            partner.save()
        except Exception as ex:
            print(item)
            print(ex.message)
            continue


def sync_audit_data():
    from internos.etools.models import Engagement, PartnerOrganization
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


def sync_trip_data():
    from internos.etools.models import Engagement, PartnerOrganization, Travel
    for page in range(320, 350):
        print(page)
        api_func = '/api/t2f/travels/?page={}&page_size={}'.format(page, 100)
        instances = get_data('etools.unicef.org', api_func, 'Token 36f06547a4b930c6608e503db49f1e45305351c2')
        instances = json.loads(instances)
        for item in instances['data']:

            instance, new_instance = Travel.objects.get_or_create(id=item['id'])

            instance.reference_number = item['reference_number']
            instance.traveler_name = item['traveler']
            instance.purpose = item['purpose']
            instance.status = item['status']
            instance.start_date = item['start_date']
            instance.end_date = item['end_date']
            instance.supervisor_name = item['supervisor_name']

            instance.save()
            # sync_trip_individual_data(instance)


def sync_trip_individual_data(instance):
    from internos.etools.models import TravelActivity, PartnerOrganization, PCA
    data = get_data('etools.unicef.org', '/api/t2f/travels/{}/'.format(instance.id),
                    'Token 36f06547a4b930c6608e503db49f1e45305351c2')
    item = json.loads(data)
    print(item['attachments'])

    instance.international_travel = item['international_travel']
    instance.ta_required = item['ta_required']
    instance.itinerary_set = item['itinerary']
    instance.activities_set = item['activities']
    for activity in item['activities']:
        instance.travel_type = activity['travel_type'].lower()
        act_instance, new_instance = TravelActivity.objects.get_or_create(id=activity['id'])

        act_instance.travel_type = activity['travel_type'].lower()
        if activity['date']:
            act_instance.date = activity['date']
        else:
            act_instance.date = instance.start_date
        act_instance.is_primary_traveler = activity['is_primary_traveler']
        act_instance.travel = instance

        if activity['partner']:
            act_instance.partner = PartnerOrganization.objects.get(etl_id=activity['partner'])

        if activity['partnership']:
            act_instance.partnership = PCA.objects.get(etl_id=activity['partnership'])

        act_instance.save()

    instance.mode_of_travel = item['mode_of_travel']
    instance.estimated_travel_cost = item['estimated_travel_cost']
    instance.completed_at = item['completed_at']
    instance.canceled_at = item['canceled_at']
    instance.rejection_note = item['rejection_note']
    instance.cancellation_note = item['cancellation_note']
    instance.attachments_set = item['attachments']
    instance.attachments_sets = item['attachments']
    instance.certification_note = item['certification_note']
    instance.report = item['report']
    instance.additional_note = item['additional_note']
    instance.misc_expenses = item['misc_expenses']
    instance.first_submission_date = item['first_submission_date']

    instance.save()


def get_data(url, apifunc, token, protocol='HTTPS'):

    # headers = {"Content-type": "application/json", "Authorization": token}
    headers = {"Content-type": "application/json",
               "Authorization": token,
               "HTTP_REFERER": "etools.unicef.org",
               # "Cookie": "tfUDK97TJSCkB4Nlm2wuMx67XNOYWpKT18BeV3RNoeq6nO7FXemAZypct369yF9I",
               # "X-CSRFToken": 'tfUDK97TJSCkB4Nlm2wuMx67XNOYWpKT18BeV3RNoeq6nO7FXemAZypct369yF9I',
               # "username": "achamseddine@unicef.org", "password": "Alouche21!"
               }

    if protocol == 'HTTPS':
        conn = httplib.HTTPSConnection(url)
    else:
        conn = httplib.HTTPConnection(url)
    conn.request('GET', apifunc, "", headers)
    response = conn.getresponse()
    result = response.read()

    if not response.status == 200:
        if response.status == 400 or response.status == 403:
            raise Exception(str(response.status) + response.reason + response.read())
        else:
            raise Exception(str(response.status) + response.reason)

    conn.close()

    return result


def link_partner_to_partnership():
    from internos.etools.models import PartnerOrganization, PCA

    partnerships = PCA.objects.all()

    for pca in partnerships:
        try:
            partner = PartnerOrganization.objects.get(name=pca.partner_name)
            pca.partner = partner
            pca.save()
        except Exception as ex:
            continue
