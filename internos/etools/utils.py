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
