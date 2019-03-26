
import logging

from internos.taskapp.celery import app
from .client import ActivityInfoClient
from .utils import r_script_command_line

logger = logging.getLogger(__name__)

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


@app.task
def link_partners(report_type=None):
    from .utils import link_ai_partners, link_etools_partners
    link_ai_partners(report_type=report_type)
    link_etools_partners()


@app.task
def import_data_and_generate_monthly_report():
    from internos.activityinfo.models import Database
    from .utils import import_data_via_r_script, link_indicators_data, calculate_indicators_values

    databases = Database.objects.filter(reporting_year__current=True)
    for db in databases:
        logger.info('1. Import report: '+db.name)
        import_data_via_r_script(db)
        logger.info('2. Link data: ' + db.name)
        link_indicators_data(db)
        logger.info('3. Calculate indicator values')
        calculate_indicators_values(db)


@app.task
def import_data_and_generate_live_report():
    from internos.activityinfo.models import Database
    from .utils import import_data_via_r_script, link_indicators_data, calculate_indicators_values

    databases = Database.objects.filter(reporting_year__current=True)
    for db in databases:
        print(db.name)
        logger.info('1. Import report: '+db.name)
        import_data_via_r_script(db, report_type='live')
        logger.info('2. Link data: ' + db.name)
        link_indicators_data(db, report_type='live')
        logger.info('3. Calculate indicator values')
        calculate_indicators_values(db, report_type='live')


@app.task
def copy_indicators_values_to_hpm():
    from internos.activityinfo.models import Indicator

    indicators = Indicator.objects.all()

    for indicator in indicators:
        indicator.values_hpm = indicator.values
        indicator.save()
