import json
import httplib
import datetime
from time import mktime


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


def get_partner_profile_details():
    from django.db import connection
    from .models import Engagement, Travel, PCA

    partners = {}
    interventions = []
    programmatic_visits = []
    audits = []
    micro_assessments = []
    spot_checks = []
    special_audits = []
    now = datetime.datetime.now()

    cursor = connection.cursor()
    cursor.execute(
        "SELECT id, etl_id, name, short_name, description, partner_type, rating, vendor_number, comments " 
        "FROM public.etools_partnerorganization "
        "WHERE hidden = false AND deleted_flag = false")

    rows = cursor.fetchall()
    for row in rows:
        partners[row[0]] = {
            'db_id': row[0],
            'id': row[1],
            'name': row[2],
            'vendor_number': row[7],
            'short_name': row[3],
            'description': row[4],
            'partner_type': row[5],
            'rating': row[6],
            'comments': row[8],
            'interventions': [],
            'interventions_active': [],
            'pds': [],
            'pds_active': [],
            'sffas': [],
            'sffas_active': [],
            'programmatic_visits': [],
            'programmatic_visits_planned': [],
            'programmatic_visits_submitted': [],
            'programmatic_visits_approved': [],
            'programmatic_visits_completed': [],
            'programmatic_visits_canceled': [],
            'programmatic_visits_rejected': [],
            'audits': [],
            'micro_assessments': [],
            'spot_checks': [],
            'special_audits': [],
        }

    #  interventions
    cursor.execute(
        "SELECT etl_id, partner_id, number, start, end_date, document_type, total_unicef_budget, "
        "budget_currency, total_budget, offices_names, location_p_codes, status " 
        "FROM public.etools_pca "
        "WHERE date_part('year', end_date) = %s AND status <> %s "
        "ORDER BY start", [now.year, PCA.CANCELLED])

    rows = cursor.fetchall()
    for row in rows:
        if row[1] in partners:
            partners[row[1]]['interventions'].append({
                'etl_id': row[0],
                'partner_id': row[1],
                'number': row[2],
                'start': row[3],
                'end_date': row[4],
                'document_type': row[5],
                'total_unicef_budget': row[6],
                'budget_currency': row[7],
                'total_budget': row[8],
                'offices_names': row[9],
                'location_p_codes': row[10],
                'status': row[11]
            })

    #  Active interventions
    cursor.execute(
        "SELECT etl_id, partner_id, number, start, end_date, document_type, total_unicef_budget, "
        "budget_currency, total_budget, offices_names, location_p_codes, status " 
        "FROM public.etools_pca "
        "WHERE date_part('year', end_date) = %s AND status = %s "
        "ORDER BY start", [now.year, PCA.ACTIVE])

    rows = cursor.fetchall()
    for row in rows:
        if row[1] in partners:
            partners[row[1]]['interventions_active'].append({
                'etl_id': row[0],
                'partner_id': row[1],
                'number': row[2],
                'start': row[3],
                'end_date': row[4],
                'document_type': row[5],
                'total_unicef_budget': row[6],
                'budget_currency': row[7],
                'total_budget': row[8],
                'offices_names': row[9],
                'location_p_codes': row[10],
                'status': row[11]
            })

    #  PDs
    cursor.execute(
        "SELECT etl_id, partner_id, number, start, end_date, document_type, total_unicef_budget, "
        "budget_currency, total_budget, offices_names, location_p_codes, status " 
        "FROM public.etools_pca "
        "WHERE date_part('year', end_date) = %s AND status <> %s AND document_type = %s "
        "ORDER BY start", [now.year, PCA.CANCELLED, PCA.PD])

    rows = cursor.fetchall()
    for row in rows:
        if row[1] in partners:
            partners[row[1]]['pds'].append({
                'etl_id': row[0],
                'partner_id': row[1],
                'number': row[2],
                'start': row[3],
                'end_date': row[4],
                'document_type': row[5],
                'total_unicef_budget': row[6],
                'budget_currency': row[7],
                'total_budget': row[8],
                'offices_names': row[9],
                'location_p_codes': row[10],
                'status': row[11]
            })

    #  Active PDs
    cursor.execute(
        "SELECT etl_id, partner_id, number, start, end_date, document_type, total_unicef_budget, "
        "budget_currency, total_budget, offices_names, location_p_codes, status " 
        "FROM public.etools_pca "
        "WHERE date_part('year', end_date) = %s AND status = %s AND document_type = %s "
        "ORDER BY start", [now.year, PCA.ACTIVE, PCA.PD])

    rows = cursor.fetchall()
    for row in rows:
        if row[1] in partners:
            partners[row[1]]['pds_active'].append({
                'etl_id': row[0],
                'partner_id': row[1],
                'number': row[2],
                'start': row[3],
                'end_date': row[4],
                'document_type': row[5],
                'total_unicef_budget': row[6],
                'budget_currency': row[7],
                'total_budget': row[8],
                'offices_names': row[9],
                'location_p_codes': row[10],
                'status': row[11]
            })

    # SFFAs
    cursor.execute(
        "SELECT etl_id, partner_id, number, start, end_date, document_type, total_unicef_budget, "
        "budget_currency, total_budget, offices_names, location_p_codes, status " 
        "FROM public.etools_pca "
        "WHERE date_part('year', end_date) = %s AND status <> %s AND document_type = %s "
        "ORDER BY start", [now.year, PCA.CANCELLED, PCA.SSFA])

    rows = cursor.fetchall()
    for row in rows:
        if row[1] in partners:
            partners[row[1]]['sffas'].append({
                'etl_id': row[0],
                'partner_id': row[1],
                'number': row[2],
                'start': row[3],
                'end_date': row[4],
                'document_type': row[5],
                'total_unicef_budget': row[6],
                'budget_currency': row[7],
                'total_budget': row[8],
                'offices_names': row[9],
                'location_p_codes': row[10],
                'status': row[11]
            })

    #  Active SFFAs
    cursor.execute(
        "SELECT etl_id, partner_id, number, start, end_date, document_type, total_unicef_budget, "
        "budget_currency, total_budget, offices_names, location_p_codes, status " 
        "FROM public.etools_pca "
        "WHERE date_part('year', end_date) = %s AND status = %s AND document_type = %s "
        "ORDER BY start", [now.year, PCA.ACTIVE, PCA.SSFA])

    rows = cursor.fetchall()
    for row in rows:
        if row[1] in partners:
            partners[row[1]]['sffas_active'].append({
                'etl_id': row[0],
                'partner_id': row[1],
                'number': row[2],
                'start': row[3],
                'end_date': row[4],
                'document_type': row[5],
                'total_unicef_budget': row[6],
                'budget_currency': row[7],
                'total_budget': row[8],
                'offices_names': row[9],
                'location_p_codes': row[10],
                'status': row[11]
            })

    #  programmatic_visits
    cursor.execute(
        "SELECT ta.id, ta.partner_id, ta.partnership_id, pc.number, tl.status, tl.attachments_sets " 
        "FROM public.etools_travelactivity ta, public.etools_pca pc, public.etools_travel tl "
        "WHERE ta.partnership_id = pc.id AND ta.travel_id = tl.id "
        "AND ta.travel_type='programmatic visit' AND date_part('year', ta.date) = %s "
        "AND (tl.status = %s OR tl.status = %s OR tl.status = %s OR tl.status = %s)"
        "ORDER BY ta.date", [now.year, Travel.PLANNED, Travel.SUBMITTED, Travel.APPROVED, Travel.COMPLETED])

    rows = cursor.fetchall()
    for row in rows:
        if row[1] in partners:
            partners[row[1]]['programmatic_visits'].append({
                'id': row[0],
                'partner_id': row[1],
                'partnership_id': row[2],
                'number': row[3],
                'status': row[4],
                'attachments_sets': row[5],
            })

    #  programmatic_visits_planned
    cursor.execute(
        "SELECT ta.id, ta.partner_id, ta.partnership_id, pc.number, tl.status, tl.attachments_sets, "
        "tl.reference_number, ta.date " 
        "FROM public.etools_travelactivity ta, public.etools_pca pc, public.etools_travel tl "
        "WHERE ta.partnership_id = pc.id AND ta.travel_id = tl.id "
        "AND ta.travel_type='programmatic visit' AND date_part('year', ta.date) = %s "
        "AND tl.status = %s "
        "ORDER BY ta.date", [now.year, Travel.PLANNED])

    rows = cursor.fetchall()
    for row in rows:
        if row[1] in partners:
            partners[row[1]]['programmatic_visits_planned'].append({
                'id': row[0],
                'partner_id': row[1],
                'partnership_id': row[2],
                'number': row[3],
                'status': row[4],
                'attachments_sets': row[5],
                'reference_number': '{} - {}'.format(row[6], row[7]),
            })

    #  programmatic_visits_submitted
    cursor.execute(
        "SELECT ta.id, ta.partner_id, ta.partnership_id, pc.number, tl.status, tl.attachments_sets, "
        "tl.reference_number, ta.date " 
        "FROM public.etools_travelactivity ta, public.etools_pca pc, public.etools_travel tl "
        "WHERE ta.partnership_id = pc.id AND ta.travel_id = tl.id "
        "AND ta.travel_type='programmatic visit' AND date_part('year', ta.date) = %s "
        "AND tl.status = %s "
        "ORDER BY ta.date", [now.year, Travel.SUBMITTED])

    rows = cursor.fetchall()
    for row in rows:
        if row[1] in partners:
            partners[row[1]]['programmatic_visits_submitted'].append({
                'id': row[0],
                'partner_id': row[1],
                'partnership_id': row[2],
                'number': row[3],
                'status': row[4],
                'attachments_sets': row[5],
                'reference_number': '{} - {}'.format(row[6], row[7]),
            })

    #  programmatic_visits_approved
    cursor.execute(
        "SELECT ta.id, ta.partner_id, ta.partnership_id, pc.number, tl.status, tl.attachments_sets, "
        "tl.reference_number, ta.date " 
        "FROM public.etools_travelactivity ta, public.etools_pca pc, public.etools_travel tl "
        "WHERE ta.partnership_id = pc.id AND ta.travel_id = tl.id "
        "AND ta.travel_type='programmatic visit' AND date_part('year', ta.date) = %s "
        "AND tl.status = %s "
        "ORDER BY ta.date", [now.year, Travel.APPROVED])

    rows = cursor.fetchall()
    for row in rows:
        if row[1] in partners:
            partners[row[1]]['programmatic_visits_approved'].append({
                'id': row[0],
                'partner_id': row[1],
                'partnership_id': row[2],
                'number': row[3],
                'status': row[4],
                'attachments_sets': row[5],
                'reference_number': '{} - {}'.format(row[6], row[7]),
            })

    #  programmatic_visits_completed
    cursor.execute(
        "SELECT ta.id, ta.partner_id, ta.partnership_id, pc.number, tl.status, tl.attachments_sets, "
        "tl.reference_number, ta.date " 
        "FROM public.etools_travelactivity ta, public.etools_pca pc, public.etools_travel tl "
        "WHERE ta.partnership_id = pc.id AND ta.travel_id = tl.id "
        "AND ta.travel_type='programmatic visit' AND date_part('year', ta.date) = %s "
        "AND tl.status = %s "
        "ORDER BY ta.date", [now.year, Travel.COMPLETED])

    rows = cursor.fetchall()
    for row in rows:
        if row[1] in partners:
            partners[row[1]]['programmatic_visits_completed'].append({
                'id': row[0],
                'partner_id': row[1],
                'partnership_id': row[2],
                'number': row[3],
                'status': row[4],
                'attachments_sets': row[5],
                'reference_number': '{} - {}'.format(row[6], row[7]),
            })

    #  programmatic_visits_canceled
    cursor.execute(
        "SELECT ta.id, ta.partner_id, ta.partnership_id, pc.number, tl.status, tl.attachments_sets, "
        "tl.reference_number, ta.date " 
        "FROM public.etools_travelactivity ta, public.etools_pca pc, public.etools_travel tl "
        "WHERE ta.partnership_id = pc.id AND ta.travel_id = tl.id "
        "AND ta.travel_type='programmatic visit' AND date_part('year', ta.date) = %s "
        "AND tl.status = %s "
        "ORDER BY ta.date", [now.year, Travel.CANCELLED])

    rows = cursor.fetchall()
    for row in rows:
        if row[1] in partners:
            partners[row[1]]['programmatic_visits_canceled'].append({
                'id': row[0],
                'partner_id': row[1],
                'partnership_id': row[2],
                'number': row[3],
                'status': row[4],
                'attachments_sets': row[5],
                'reference_number': '{} - {}'.format(row[6], row[7]),
            })

    #  programmatic_visits_rejected
    cursor.execute(
        "SELECT ta.id, ta.partner_id, ta.partnership_id, pc.number, tl.status, tl.attachments_sets, "
        "tl.reference_number, ta.date " 
        "FROM public.etools_travelactivity ta, public.etools_pca pc, public.etools_travel tl "
        "WHERE ta.partnership_id = pc.id AND ta.travel_id = tl.id "
        "AND ta.travel_type='programmatic visit' AND date_part('year', ta.date) = %s "
        "AND tl.status = %s "
        "ORDER BY ta.date", [now.year, Travel.REJECTED])

    rows = cursor.fetchall()
    for row in rows:
        if row[1] in partners:
            partners[row[1]]['programmatic_visits_rejected'].append({
                'id': row[0],
                'partner_id': row[1],
                'partnership_id': row[2],
                'number': row[3],
                'status': row[4],
                'attachments_sets': row[5],
                'reference_number': '{} - {}'.format(row[6], row[7]),
            })

    #  micro_assessments
    cursor.execute(
        "SELECT id, partner_id, findings_sets, internal_controls, displayed_name " 
        "FROM public.etools_engagement "
        "WHERE engagement_type = %s AND status <> %s AND date_part('year', start_date) = %s "
        "ORDER BY start_date", [Engagement.TYPE_MICRO_ASSESSMENT, Engagement.CANCELLED, now.year])

    rows = cursor.fetchall()
    for row in rows:
        if row[1] in partners:
            partners[row[1]]['micro_assessments'].append({
                'id': row[0],
                'partner_id': row[1],
                'findings_sets': row[2],
                'internal_controls': row[3],
                'displayed_name': row[4]
            })

    #  spot_checks
    cursor.execute(
        "SELECT id, partner_id, findings_sets, internal_controls, displayed_name " 
        "FROM public.etools_engagement "
        "WHERE engagement_type = %s AND status <> %s AND date_part('year', start_date) = %s "
        "ORDER BY start_date", [Engagement.TYPE_SPOT_CHECK, Engagement.CANCELLED, now.year])

    rows = cursor.fetchall()
    for row in rows:
        if row[1] in partners:
            partners[row[1]]['spot_checks'].append({
                'id': row[0],
                'partner_id': row[1],
                'findings_sets': row[2],
                'internal_controls': row[3],
                'displayed_name': row[4]
            })

    #  audits
    cursor.execute(
        "SELECT id, partner_id, findings_sets, internal_controls, displayed_name " 
        "FROM public.etools_engagement "
        "WHERE engagement_type = %s AND status <> %s AND date_part('year', start_date) = %s "
        "ORDER BY start_date", [Engagement.TYPE_AUDIT, Engagement.CANCELLED, now.year])

    rows = cursor.fetchall()
    for row in rows:
        if row[1] in partners:
            partners[row[1]]['audits'].append({
                'id': row[0],
                'partner_id': row[1],
                'findings_sets': row[2],
                'internal_controls': row[3],
                'displayed_name': row[4]
            })

    #  special_audits
    cursor.execute(
        "SELECT id, partner_id, findings_sets, internal_controls, displayed_name " 
        "FROM public.etools_engagement "
        "WHERE engagement_type = %s AND status <> %s AND date_part('year', start_date) = %s "
        "ORDER BY start_date", [Engagement.TYPE_SPECIAL_AUDIT, Engagement.CANCELLED, now.year])

    rows = cursor.fetchall()
    for row in rows:
        if row[1] in partners:
            partners[row[1]]['special_audits'].append({
                'id': row[0],
                'partner_id': row[1],
                'findings_sets': row[2],
                'internal_controls': row[3],
                'displayed_name': row[4]
            })

    return partners


def get_trip_details(data_set):
    details = {'visits': [], 'locations': []}
    for visit in data_set:
        travel = visit.travel
        for location in visit.locations.filter(point__isnull=False).iterator():
            details['locations'].append({
                'name': location.name,
                'latitude': location.point.x,
                'longitude': location.point.y,
            })
        if travel.section and travel.office:
            key = '{}-{}'.format(travel.section.name, travel.office.name)
            if key not in details:
                details[key] = 1
            else:
                details[key] += 1

        if travel.section:
            if travel.section.name not in details:
                details[travel.section.name] = 1
            else:
                details[travel.section.name] += 1

        if travel.office:
            if travel.office.name not in details:
                details[travel.office.name] = 1
            else:
                details[travel.office.name] += 1

        details['visits'].append(visit)
        print(details)

    return details
