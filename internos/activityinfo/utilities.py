from .client import ActivityInfoClient
from .models import *
import copy

"""  Reformatting json structure for each database  """


def import_data_v4(ai_db):
    client = ActivityInfoClient(ai_db.username, ai_db.password)
    # main_db_id = ReportingYear.objects.get(current=True).database_id
    main_db_id = ai_db.reporting_year.database_id
    db_info = client.get_databases_v4(main_db_id)
    resources = db_info['resources']
    new_data = {}

    for item in resources:
        if item['parentId'] == ai_db.db_id:
            if item['type'] == 'FOLDER':
                if 'Folders' not in new_data:
                    new_data['Folders'] = []
                new_data['Folders'].append(item)
            if item['type'] == 'FORM':
                if 'Forms' not in new_data:
                    new_data['Forms'] = []
                new_data['Forms'].append(item)

    if 'Folders' in new_data:
        for entry in new_data['Folders']:
            for item in resources:
                if item['parentId'] == entry['id'] and item['type'] == 'FORM':
                    if 'Forms' not in entry:
                        entry['Forms'] = []
                    entry['Forms'].append(item)

    if 'Folders' not in new_data:
        if 'Forms' in new_data:
            for form in new_data['Forms']:
                for item in resources:
                    if item['parentId'] == form['id'] and item['type'] == 'SUB_FORM':
                        if 'Sub_Forms' not in form:
                            form['Sub_Forms'] = []
                        form['Sub_Forms'].append(item)

    if 'Folders' in new_data:
        for folder in new_data['Folders']:
            if 'Forms' in folder:
                for form in folder['Forms']:
                    for item in resources:
                        if item['parentId'] == form['id'] and item['type'] == 'SUB_FORM':
                            if 'Sub_Forms' not in form:
                                form['Sub_Forms'] = []
                            form['Sub_Forms'].append(item)
    json_data = new_data

    if 'Folders' in json_data:
        for folder in json_data['Folders']:
            if 'Forms' in folder:
                for form in folder['Forms']:
                    # try:
                    #     ai_activity = Activity.objects.get(ai_form_id=form['id'])
                    # except Activity.DoesNotExist:
                    #     ai_activity = Activity(ai_form_id=form['id'])

                    ai_activity, created = Activity.objects.get_or_create(ai_form_id=form['id'],
                                                                          database_id=ai_db.id)
                    ai_activity.name = form['label']
                    # ai_activity.database = ai_db
                    ai_activity.category = folder['label']
                    ai_activity.ai_category_id = form['parentId']
                    ai_activity.save()
                    """ get indicators list for each form"""
                    get_list_indicators_v4(ai_db, form['id'], ai_activity)

    if 'Forms' in json_data:
        for form in json_data['Forms']:
            # try:
            #     ai_activity = Activity.objects.get(ai_form_id=form['id'])
            # except Activity.DoesNotExist:
            #     ai_activity = Activity(ai_form_id=form['id'])

            ai_activity, created = Activity.objects.get_or_create(ai_form_id=form['id'],
                                                                  database_id=ai_db.id)

            ai_activity.name = form['label']
            # ai_activity.database = ai_db
            ai_activity.save()
            """ get indicators list for each form"""
            get_list_indicators_v4(ai_db, form['id'], ai_activity)
    return len(new_data)


def import_partners(ai_db):
    from datetime import date
    client = ActivityInfoClient(ai_db.username, ai_db.password)
    form_id = ReportingYear.objects.get(current=True).form_id
    db_info = client.get_partners(form_id)
    for item in db_info:
        try:
            partner = Partner.objects.get(ai_id=item['@id'], year=date.today().year)
        except Partner.DoesNotExist:
            partner = Partner(ai_id=item['@id'])
        partner.name = item['Name']
        partner.full_name = item['Partner full name'] if 'Partner full name' in item else ''
        partner.year = date.today().year
        partner.save()
    return len(db_info)


def get_list_indicators_v4(ai_db, form_id, ai_activity):
    from .utils import get_awp_code
    client = ActivityInfoClient(ai_db.username, ai_db.password)
    form_info = client.get_database_indicators_v4(form_id)
    form_elements = form_info['elements']
    # sub_form_id = list(filter(lambda x: "Monthly Reporting" in x['label'], form_elements))
    sub_form_id = list(filter(lambda x: "subform" in x['type'], form_elements))
    if sub_form_id is not None and len(sub_form_id) > 0:
        indicator_id = sub_form_id[0]['typeParameters']['formId']
        indicator_all_info = client.get_database_indicators_v4(indicator_id)
        indicator_list = indicator_all_info['elements']
        sub_indicators = [x for x in indicator_list if x['type'] == 'quantity']
        for sub_indicator in sub_indicators:

            # try:
            #     ai_sub_indicator = Indicator.objects.get(ai_indicator=sub_indicator['id'])
            # except Indicator.DoesNotExist:
            #     ai_sub_indicator = Indicator(ai_indicator=sub_indicator['id'])
            # except Indicator.MultipleObjectsReturned:
            #     continue

            ai_sub_indicator, created = Indicator.objects.get_or_create(ai_indicator=sub_indicator['id'],
                                                                        activity_id=ai_activity.id)

            ai_sub_indicator.description = sub_indicator['description'] if 'description' in sub_indicator else ''
            ai_sub_indicator.label = sub_indicator['label']
            ai_sub_indicator.name = sub_indicator['label']
            ai_sub_indicator.type = sub_indicator['type'] if 'type' in sub_indicator else ''
            # ai_sub_indicator.activity = Activity.objects.get(ai_form_id=form_id)
            # ai_sub_indicator.activity = ai_activity
            ai_sub_indicator.units = sub_indicator['typeParameters']['units']
            ai_sub_indicator.master_indicator = False
            ai_sub_indicator.awp_code = get_awp_code(sub_indicator['label'])
            ai_sub_indicator.category = ''
            ai_sub_indicator.save()


#
# def get_indicators_v4(ai_db, form_id):
#     client = ActivityInfoClient(ai_db.username, ai_db.password)
#     form_info = client.get_database_indicators_v4(form_id)
#     form_elements = form_info['elements']
#     sub_form_id = list(filter(lambda x: "Monthly Reporting" in x['label'], form_elements))
#     indicator_id = sub_form_id[0]['typeParameters']['formId']
#     indicator_all_info = client.get_database_indicators_v4(indicator_id)
#     indicator_list = indicator_all_info['elements']
#     category_indicators = [x for x in indicator_list if x['type'] == 'enumerated' and (
#             x['relevanceCondition'] == "" or x['relevanceCondition'] is None)]
#
#     sub_indicators = [x for x in indicator_list if x['type'] == 'quantity']
#     for sub_indicator in sub_indicators:
#         try:
#             ai_sub_indicator = Indicator.objects.get(ai_indicator=sub_indicator['id'])
#         except Indicator.DoesNotExist:
#             ai_sub_indicator = Indicator(ai_indicator=sub_indicator['id'])
#         ai_sub_indicator.description = sub_indicator['description'] if 'description' in sub_indicator else ''
#         ai_sub_indicator.label = sub_indicator['label']
#         ai_sub_indicator.name = sub_indicator['label']
#         ai_sub_indicator.type = sub_indicator['type'] if 'type' in sub_indicator else ''
#         ai_sub_indicator.activity = Activity.objects.get(ai_form_id=form_id)
#         ai_sub_indicator.units = sub_indicator['typeParameters']['units']
#         ai_sub_indicator.master_indicator = False
#         ai_sub_indicator.save()
#         if len(sub_indicator['relevanceCondition']) > 0:
#             master_id = sub_indicator['relevanceCondition'].split(".")[0]
#             master_indicator = [x for x in indicator_list if (x['type'] == 'enumerated' and x['id'] == master_id and (
#                     x['relevanceCondition'] is not None and x['relevanceCondition'] != ""))]
#
#         if master_indicator is not None and len(master_indicator) > 0:
#             master_ai_id = master_indicator[0]['typeParameters']['values'][0]['id']
#             master_name = master_indicator[0]['typeParameters']['values'][0]['label']
#             if len(master_name) < 10:
#                 master_name = master_indicator[0]['label']
#             try:
#                 ai_indicator = Indicator.objects.get(ai_indicator=master_ai_id)
#             except Indicator.DoesNotExist:
#                 ai_indicator = Indicator(ai_indicator=master_ai_id)
#             ai_indicator.description = master_indicator['description'] if 'description' in master_indicator else ''
#             ai_indicator.label = master_name
#             ai_indicator.name = master_name
#             ai_indicator.type = master_indicator['type'] if 'type' in master_indicator else ''
#             ai_indicator.activity = Activity.objects.get(ai_form_id=form_id)
#             category_id = master_indicator[0]['relevanceCondition'].split(".")[0]
#             category = [x for x in category_indicators if x['id'] == category_id]
#
#             if len(category) > 0:
#                 if len(category[0]['label']) > 15:
#                     ai_indicator.category = category[0]['label']
#                 elif len(category[0]['typeParameters']['values'][0]['label']) > 15:
#                     ai_indicator.category = category[0]['typeParameters']['values'][0]['label']
#                 else:
#                     ai_indicator.category = ''
#
#             ai_indicator.master_indicator = True
#             ai_sub_indicator.category = ai_indicator.category
#             ai_sub_indicator.save()
#             ai_indicator.save()
#             ai_indicator.sub_indicators.add(ai_sub_indicator)
#         else:
#             category_id = sub_indicator['relevanceCondition'].split(".")[0]
#             category = [x for x in category_indicators if x['id'] == category_id]
#             if len(category) > 0:
#                 if len(category[0]['label']) > 15:
#                     ai_sub_indicator.category = category[0]['label']
#                 else:
#                     ai_sub_indicator.category = category[0]['typeParameters']['values'][0]['label']
#                     ai_sub_indicator.save()
