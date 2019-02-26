
from internos.taskapp.celery import app
from .client import ActivityInfoClient
from .utils import r_script_command_line


def read_form_data(formid):
    client = ActivityInfoClient()
    response = client.make_request('resources/form/M2142704628/query/rows').json()
    print(response)


@app.task
def exec_import_script():
    from .models import Database

    databases = Database.objects.all()
    for db in databases:
        r_script_command_line('ai_generate_excel.R', db.ai_id)


def read_imported_data():
    from .models import Database

    databases = Database.objects.all()
    for db in databases:
        pass
        # r_script_command_line('ai_generate_excel.R', db.ai_id)


@app.task
def import_live_data():
    from internos.activityinfo.models import Database

    databases = Database.objects.filter(reporting_year__current=True)
    for db in databases:
        print('1. Import report')
        r_script_command_line('ai_generate_excel.R', db)


@app.task
def calculate_live_values():
    from internos.activityinfo.utils import sync_live_data, link_indicators_data, reset_indicators_values, calculate_indicators_values
    from internos.activityinfo.models import Database

    databases = Database.objects.filter(reporting_year__current=True)
    for db in databases:
        print('1. Import data forced')
        sync_live_data(db)
        print('2. Link indicators')
        link_indicators_data(db, report_type='live')
        print('3. Reset values')
        reset_indicators_values(db.ai_id, report_type='live')
        # print('4. Calculate indicator values')
        # calculate_indicators_values(db, report_type='live')
