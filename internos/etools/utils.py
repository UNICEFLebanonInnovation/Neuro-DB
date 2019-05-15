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
        "SELECT id, etl_id, name, short_name, description, partner_type, rating, vendor_number, comments, "
        "shared_partner, total_ct_ytd, type_of_assessment " 
        "FROM public.etools_partnerorganization "
        "WHERE hidden = false AND deleted_flag = false "
        "ORDER BY name ")

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
            'shared_partner': row[9],
            'total_ct_ytd': row[10],
            'type_of_assessment': row[11],
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
            'audits_completed': [],
            'micro_assessments': [],
            'spot_checks': [],
            'spot_checks_completed': [],
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
                'displayed_name': row[4],
                'action_points': get_action_points_details('audit_sc', row[0])
            })

    #  spot_checks
    cursor.execute(
        "SELECT id, partner_id, findings_sets, internal_controls, displayed_name " 
        "FROM public.etools_engagement "
        "WHERE engagement_type = %s AND status = %s AND date_part('year', start_date) = %s "
        "ORDER BY start_date", [Engagement.TYPE_SPOT_CHECK, Engagement.FINAL, now.year])

    rows = cursor.fetchall()
    for row in rows:
        if row[1] in partners:
            partners[row[1]]['spot_checks_completed'].append({
                'id': row[0],
                'partner_id': row[1],
                'findings_sets': row[2],
                'internal_controls': row[3],
                'displayed_name': row[4],
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

    #  audits
    cursor.execute(
        "SELECT id, partner_id, findings_sets, internal_controls, displayed_name " 
        "FROM public.etools_engagement "
        "WHERE engagement_type = %s AND status = %s AND date_part('year', start_date) = %s "
        "ORDER BY start_date", [Engagement.TYPE_AUDIT, Engagement.FINAL, now.year])

    rows = cursor.fetchall()
    for row in rows:
        if row[1] in partners:
            partners[row[1]]['audits_completed'].append({
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
                'travel': travel.reference_number,
                'travel_url': 'https://etools.unicef.org/t2f/edit-travel/{}'.format(travel.id),
                'section': travel.section.name if travel.section else '',
                'office': travel.office.name if travel.office else '',
                'traveler_name': travel.traveler_name,
                'latitude': location.point.y,
                'longitude': location.point.x,
            })
        if travel.section and travel.office:
            key = '{}-{}'.format(travel.section.name, travel.office.name)
            if key not in details:
                details[key] = []
            details[key].append({
                'reference_number': travel.reference_number,
                'purpose': travel.purpose,
                'id': travel.id,
                'traveler_name': travel.traveler_name,
                'date': travel.start_date,
            })

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

    details['locations'] = json.dumps(details['locations'])

    return details


def get_action_points_details(related_module, related_module_id):
    from internos.etools.models import ActionPoint

    data = []
    action_points = []
    if related_module.startswith('audit'):
        action_points = ActionPoint.objects.filter(related_module=related_module, engagement_id=related_module_id)

    for point in action_points.iterator():
        data.append({
            'id': point.id,
            'reference_number': point.reference_number,
            'description': point.description,
            'due_date': point.due_date,
            'author_name': point.author_name,
            'assigned_by_name': point.assigned_by_name,
            'assigned_to_name': point.assigned_to_name,
            'high_priority': point.high_priority,
            'section_name': point.section.name if point.section else '',
            'office_name': point.office.name if point.office else '',
            'status': point.status,
            'status_date': point.status_date,
            'category_name': point.category_name
        })

    return data


def get_interventions_details(data_set):
    from internos.users.models import Office

    details = []
    for intervention in data_set:
        for location in intervention.locations.filter(point__isnull=False).iterator():

            separator = ', '
            section_names = separator.join(intervention.section_names)
            offices_names = []
            for office in intervention.offices:
                offices_names.append(Office.objects.get(id=int(office)).name)
            offices_names = separator.join(offices_names)

            details.append({
                'name': location.name,
                'latitude': location.point.y,
                'longitude': location.point.x,
                'title': intervention.title,
                'document_type': intervention.document_type,
                'partner_name': intervention.partner_name,
                'status': intervention.status,
                'number': intervention.number,
                'start': intervention.start.strftime("%m/%d/%Y") if intervention.start else '',
                'end_date': intervention.end_date.strftime("%m/%d/%Y") if intervention.end_date else '',
                'total_budget': '{} {}'.format(intervention.total_budget, intervention.budget_currency),
                'url': 'https://etools.unicef.org/pmp/interventions/{}'.format(intervention.etl_id),
                'section_names': section_names,
                'offices_names': offices_names,
            })

    details = json.dumps(details)

    return details
